"""Clics asistidos sobre el widget Turnstile (DOM y modo visión + YOLO)."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

if TYPE_CHECKING:
    from camoufox_turnstile.vision import YoloTurnstileDetector

log = logging.getLogger(__name__)


async def try_click_turnstile_widget(page, *, locate_timeout_ms: int) -> bool:
    """Intenta clics sobre el iframe host de Turnstile (cross-origin)."""
    iframe_sel = (
        'iframe[src*="turnstile"], iframe[src*="challenges.cloudflare.com"], '
        'iframe[src*="cloudflare.com/cdn-cgi"]'
    )
    candidates = page.locator(iframe_sel)
    try:
        await candidates.first.wait_for(state="attached", timeout=locate_timeout_ms)
    except (PlaywrightTimeoutError, PlaywrightError):
        return False

    clicked_any = False
    try:
        n = await candidates.count()
        for i in range(min(n, 5)):
            iframe = candidates.nth(i)
            if not await iframe.is_visible():
                continue
            try:
                await iframe.scroll_into_view_if_needed(timeout=locate_timeout_ms)
            except PlaywrightTimeoutError:
                pass

            box = await iframe.bounding_box()
            if not box or box.get("width", 0) < 4 or box.get("height", 0) < 4:
                try:
                    await iframe.click(timeout=locate_timeout_ms, force=True)
                    clicked_any = True
                except PlaywrightError:
                    continue
                await asyncio.sleep(0.12)
                continue

            w = float(box["width"])
            h = float(box["height"])
            bx = float(box["x"])
            by = float(box["y"])
            mid_y = by + h / 2

            page_points: list[tuple[float, float]] = [
                (bx + max(8.0, w * 0.14), mid_y),
                (bx + max(8.0, w * 0.22), mid_y),
                (bx + w * 0.5, mid_y),
                (bx + max(6.0, w * 0.08), mid_y),
            ]

            for cx, cy in page_points:
                try:
                    await page.mouse.move(cx, cy)
                    await page.mouse.click(cx, cy)
                    clicked_any = True
                    await asyncio.sleep(0.12)
                except PlaywrightError:
                    continue

            try:
                rel_x = max(10, int(w * 0.18))
                rel_y = int(h / 2)
                await iframe.click(
                    position={"x": rel_x, "y": rel_y},
                    timeout=locate_timeout_ms,
                    delay=80,
                    force=True,
                )
                clicked_any = True
                await asyncio.sleep(0.12)
            except PlaywrightError:
                pass

        return clicked_any
    except PlaywrightError:
        return clicked_any


async def assist_turnstile_clicks(
    page,
    *,
    nav_timeout_ms: int,
    iframe_wait_sec: float,
) -> None:
    locate_ms = min(10_000, max(3_000, nav_timeout_ms))
    for attempt in (1, 2):
        if attempt == 1:
            if iframe_wait_sec > 0:
                log.info(
                    "Esperando %.1fs a que cargue el iframe Turnstile…", iframe_wait_sec
                )
                await asyncio.sleep(float(iframe_wait_sec))
        ok = await try_click_turnstile_widget(page, locate_timeout_ms=locate_ms)
        log.info(
            "Clic asistido Turnstile (ronda %s/2): %s",
            attempt,
            "clics en iframe(s)" if ok else "sin iframe visible / sin hit",
        )
        if attempt == 1:
            await asyncio.sleep(0.85)


async def assist_turnstile_vision_clicks(
    page,
    *,
    nav_timeout_ms: int,
    detector: YoloTurnstileDetector,
    yolo_conf: float,
    iframe_wait_sec: float,
    skip_dom_when_success_mark: bool = True,
) -> None:
    """
    Captura + YOLO; si no hay clic útil, heurística de iframe.

    Si ``skip_dom_when_success_mark`` es True y YOLO devuelve solo ``success_mark``,
    no se ejecuta el fallback DOM (comportamiento recomendado del SDK).
    """
    from camoufox_turnstile.vision import decode_screenshot_png

    locate_ms = min(10_000, max(3_000, nav_timeout_ms))
    for attempt in (1, 2):
        if attempt == 1:
            if iframe_wait_sec > 0:
                log.info(
                    "Esperando %.1fs a que cargue el iframe Turnstile…", iframe_wait_sec
                )
                await asyncio.sleep(float(iframe_wait_sec))
        vp = page.viewport_size
        vw, vh = int(vp["width"]), int(vp["height"])
        yolo_clicked = False
        success_only = False
        try:
            png = await page.screenshot(type="png")
            img = decode_screenshot_png(png)
            res = detector.suggest(
                img,
                viewport_css_width=vw,
                viewport_css_height=vh,
                conf_min=float(yolo_conf),
            )
            if res.should_click and res.click_page is not None:
                cx, cy = res.click_page
                await page.mouse.move(cx, cy)
                await page.mouse.click(cx, cy)
                yolo_clicked = True
                log.info(
                    "Clic YOLO (%s conf=%.2f) en página (%.1f, %.1f)",
                    res.class_name,
                    res.confidence,
                    cx,
                    cy,
                )
            elif res.class_name == "success_mark":
                success_only = True
                log.info(
                    "YOLO: success_mark (conf=%.2f); sin clic en checkbox.",
                    res.confidence,
                )
            else:
                log.info(
                    "YOLO: sin clic útil (clase=%r, conf=%.2f); fallback DOM.",
                    res.class_name,
                    res.confidence,
                )
        except Exception:
            log.exception("Error captura/inferencia YOLO")

        if not yolo_clicked and not (skip_dom_when_success_mark and success_only):
            ok = await try_click_turnstile_widget(page, locate_timeout_ms=locate_ms)
            log.info(
                "Asistencia visión (ronda %s/2): sin clic YOLO; fallback DOM: %s",
                attempt,
                "clics en iframe(s)" if ok else "sin iframe / sin hit",
            )
        elif not yolo_clicked and success_only:
            log.info(
                "Asistencia visión (ronda %s/2): success_mark; sin fallback DOM.",
                attempt,
            )
        else:
            log.info(
                "Asistencia visión (ronda %s/2): clic YOLO; sin ronda DOM adicional.",
                attempt,
            )
            await asyncio.sleep(0.12)
        if attempt == 1:
            await asyncio.sleep(0.85)
