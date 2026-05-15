"""Orquestación de alto nivel: espera de token y ``solve_on_page`` con polling YOLO."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal, cast

from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from camoufox_turnstile.assist import try_click_turnstile_widget
from camoufox_turnstile.weights import ensure_yolo_weights

if TYPE_CHECKING:
    from camoufox_turnstile.vision import VisionClickResult

log = logging.getLogger(__name__)

VisualOkVia = Literal["success_mark", "token_only", "both", "none"]


class TurnstileError(Exception):
    """Error genérico del SDK Turnstile."""


class TurnstileTokenTimeout(TurnstileError, TimeoutError):
    """No apareció token en ``cf-turnstile-response`` a tiempo."""


@dataclass
class SolveOptions:
    """Parámetros de ``solve_on_page``.

    ``refresh_yolo_weights``: si es True, ignora la caché del ``.pt`` y vuelve a
    descargar (útil tras sustituir el objeto en S3 con la misma clave). También
    fuerza recarga la variable de entorno ``TURNSTILE_YOLO_FORCE_DOWNLOAD=1``.
    """

    nav_timeout_ms: int = 90_000
    token_timeout_ms: int = 120_000
    iframe_wait_sec: float = 7.0
    yolo_weights: Path | str | None = None
    yolo_conf: float = 0.4
    success_mark_conf_min: float | None = None
    vision_poll_interval_sec: float = 0.35
    max_yolo_clicks: int = 15
    max_dom_attempts: int = 2
    use_dom_fallback: bool = True
    locate_timeout_ms: int | None = None
    refresh_yolo_weights: bool = False

    def locate_ms(self) -> int:
        if self.locate_timeout_ms is not None:
            return self.locate_timeout_ms
        return min(10_000, max(3_000, self.nav_timeout_ms))


@dataclass
class SolveResult:
    token: str
    visual_ok_via: VisualOkVia
    vision_iterations: int
    checkbox_clicked: bool
    success_mark_confidence: float | None
    yolo_clicks: int
    dom_attempts: int


_TOKEN_JS = """() => {
  const el = document.querySelector('input[name="cf-turnstile-response"]');
  if (!el) return null;
  const v = (el.value || "").trim();
  return v.length ? v : null;
}"""


async def read_turnstile_token(page: Page) -> str | None:
    """Lee el token actual si existe."""
    v = await page.evaluate(_TOKEN_JS)
    return cast(str | None, v)


async def wait_turnstile_token(page: Page, *, timeout_ms: int) -> str:
    """Espera a que ``input[name="cf-turnstile-response"]`` tenga valor."""
    try:
        await page.wait_for_function(
            """() => {
                const el = document.querySelector(
                  'input[name="cf-turnstile-response"]'
                );
                return !!(el && (el.value || "").trim().length > 0);
            }""",
            timeout=timeout_ms,
        )
    except PlaywrightTimeoutError as e:
        raise TurnstileTokenTimeout(
            f"Sin token Turnstile tras {timeout_ms} ms"
        ) from e
    tok = await read_turnstile_token(page)
    if not tok:
        raise TurnstileTokenTimeout(
            f"Campo de token vacío tras wait_for_function ({timeout_ms} ms)"
        )
    return tok


def _quantize_click(res: "VisionClickResult", grid: float = 8.0) -> tuple[float, float, str] | None:
    if not res.should_click or res.click_page is None:
        return None
    cx, cy = res.click_page
    qx = round(cx / grid) * grid
    qy = round(cy / grid) * grid
    return (qx, qy, res.class_name)


async def solve_on_page(page: Page, options: SolveOptions | None = None) -> SolveResult:
    """
    Asiste el widget Turnstile en ``page`` y devuelve el token.

    Siempre ejecuta el bucle de captura + inferencia YOLO hasta obtener token o
    agotar ``token_timeout_ms``. Si ``use_dom_fallback`` es True, pueden
    ejecutarse clics heurísticos sobre el iframe cuando no hay una sugerencia
    YOLO clara.
    """
    opt = options or SolveOptions()
    sm_min = opt.success_mark_conf_min if opt.success_mark_conf_min is not None else opt.yolo_conf
    deadline = time.monotonic() + (opt.token_timeout_ms / 1000.0)

    saw_success_mark = False
    last_sm_conf: float | None = None
    checkbox_clicked = False
    yolo_clicks = 0
    dom_attempts = 0
    vision_iterations = 0
    skip_dom_rest = False
    last_click_key: tuple[float, float, str] | None = None
    it_since_click = 99

    async def remaining_ms() -> int:
        return max(0, int((deadline - time.monotonic()) * 1000))

    tok = await read_turnstile_token(page)
    if tok:
        return SolveResult(
            token=tok,
            visual_ok_via="token_only",
            vision_iterations=0,
            checkbox_clicked=False,
            success_mark_confidence=None,
            yolo_clicks=0,
            dom_attempts=0,
        )

    weights: Path
    if opt.yolo_weights is not None:
        weights = Path(opt.yolo_weights).expanduser().resolve()
    else:
        log.info(
            "Pesos YOLO: sin ruta en SolveOptions; se usa caché o descarga automática "
            "(ver camoufox_turnstile.weights.ensure_yolo_weights)."
        )
        weights = ensure_yolo_weights(force_download=opt.refresh_yolo_weights)

    from camoufox_turnstile.vision import VisionClickResult, decode_screenshot_png, load_yolo_detector

    detector = load_yolo_detector(weights)

    if opt.iframe_wait_sec > 0:
        log.info("Esperando %.1fs al iframe Turnstile…", opt.iframe_wait_sec)
        await asyncio.sleep(float(opt.iframe_wait_sec))

    vp = page.viewport_size
    if not vp:
        raise TurnstileError("La página no tiene viewport_size definido.")
    vw, vh = int(vp["width"]), int(vp["height"])
    locate_ms = opt.locate_ms()

    while time.monotonic() < deadline:
        vision_iterations += 1
        it_since_click += 1

        tok2 = await read_turnstile_token(page)
        if tok2:
            via: VisualOkVia
            if saw_success_mark:
                via = "both"
            else:
                via = "token_only"
            return SolveResult(
                token=tok2,
                visual_ok_via=via,
                vision_iterations=vision_iterations,
                checkbox_clicked=checkbox_clicked,
                success_mark_confidence=last_sm_conf,
                yolo_clicks=yolo_clicks,
                dom_attempts=dom_attempts,
            )

        try:
            png = await page.screenshot(type="png")
            img = decode_screenshot_png(png)
            res = detector.suggest(
                img,
                viewport_css_width=vw,
                viewport_css_height=vh,
                conf_min=float(opt.yolo_conf),
            )
        except Exception:
            log.exception("Fallo captura/inferencia YOLO en iteración %s", vision_iterations)
            res = VisionClickResult(
                bbox_image=None,
                click_image=None,
                click_page=None,
                confidence=0.0,
                class_name="none",
                should_click=False,
            )

        if res.class_name == "success_mark" and res.confidence >= sm_min:
            saw_success_mark = True
            last_sm_conf = res.confidence
            skip_dom_rest = True
            log.info(
                "YOLO: success_mark conf=%.2f (sin DOM ruidoso en esta fase).",
                res.confidence,
            )
        elif res.should_click and res.click_page is not None and yolo_clicks < opt.max_yolo_clicks:
            key = _quantize_click(res)
            if key is not None:
                cname = key[2]
                allow = key != last_click_key or it_since_click >= 3
                if allow:
                    cx, cy = res.click_page
                    await page.mouse.move(cx, cy)
                    await page.mouse.click(cx, cy)
                    yolo_clicks += 1
                    last_click_key = key
                    it_since_click = 0
                    if cname == "target_checkbox":
                        checkbox_clicked = True
                    log.info(
                        "Clic YOLO (%s conf=%.2f) en (%.1f, %.1f)",
                        cname,
                        res.confidence,
                        cx,
                        cy,
                    )
        elif (
            opt.use_dom_fallback
            and not skip_dom_rest
            and dom_attempts < opt.max_dom_attempts
            and res.class_name == "none"
        ):
            ok = await try_click_turnstile_widget(page, locate_timeout_ms=locate_ms)
            dom_attempts += 1
            log.info(
                "Fallback DOM (%s/%s): %s",
                dom_attempts,
                opt.max_dom_attempts,
                "clics" if ok else "sin hit",
            )

        await asyncio.sleep(max(0.05, float(opt.vision_poll_interval_sec)))

    ms = await remaining_ms()
    if ms <= 0:
        raise TurnstileTokenTimeout(
            f"Tiempo total agotado ({opt.token_timeout_ms} ms) sin token."
        )
    token = await wait_turnstile_token(page, timeout_ms=ms)
    via_end: VisualOkVia = "both" if saw_success_mark else "token_only"
    return SolveResult(
        token=token,
        visual_ok_via=via_end,
        vision_iterations=vision_iterations,
        checkbox_clicked=checkbox_clicked,
        success_mark_confidence=last_sm_conf,
        yolo_clicks=yolo_clicks,
        dom_attempts=dom_attempts,
    )
