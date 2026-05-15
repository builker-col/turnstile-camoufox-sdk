"""
Visión para localizar el widget Turnstile en capturas del viewport y sugerir clic.

Las coordenadas de ratón de Playwright son píxeles CSS de layout. La captura
``page.screenshot()`` suele coincidir en tamaño con el viewport cuando
``device_scale_factor=1``; si no, escalar con ``image_xy_to_page_xy``.

Clases YOLO esperadas (nombres leídos desde ``model.names`` del checkpoint):
``target_checkbox``, ``widget_container``, ``success_mark``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np

Strategy = Literal["heuristic_iframe", "yolo"]

CLS_TARGET = "target_checkbox"
CLS_WIDGET = "widget_container"
CLS_SUCCESS = "success_mark"


@dataclass(frozen=True)
class VisionClickResult:
    """Resultado de sugerir dónde clicar a partir de una captura."""

    bbox_image: tuple[float, float, float, float] | None
    click_image: tuple[float, float] | None
    click_page: tuple[float, float] | None
    confidence: float
    class_name: Literal[
        "target_checkbox", "widget_container", "success_mark", "none"
    ]
    should_click: bool


def decode_screenshot_png(png_bytes: bytes) -> np.ndarray:
    """Decodifica PNG a ``uint8`` RGB con forma ``(H, W, 3)``."""
    import cv2  # noqa: PLC0415

    buf = np.frombuffer(png_bytes, dtype=np.uint8)
    bgr = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError("No se pudo decodificar el PNG (cv2.imdecode devolvió None)")
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def image_xy_to_page_xy(
    cx_img: float,
    cy_img: float,
    *,
    viewport_css_width: float,
    viewport_css_height: float,
    image_width_px: int,
    image_height_px: int,
) -> tuple[float, float]:
    """Mapea un punto de la imagen de captura a coordenadas de página (CSS px)."""
    if image_width_px <= 0 or image_height_px <= 0:
        return (cx_img, cy_img)
    sx = float(viewport_css_width) / float(image_width_px)
    sy = float(viewport_css_height) / float(image_height_px)
    return (cx_img * sx, cy_img * sy)


def bbox_css_to_bbox_image(
    box: dict[str, float],
    *,
    viewport_css_width: float,
    viewport_css_height: float,
    image_width_px: int,
    image_height_px: int,
) -> tuple[float, float, float, float]:
    """Proyecta ``bounding_box()`` del iframe (CSS página) a píxeles de imagen."""
    bx = float(box["x"])
    by = float(box["y"])
    bw = float(box["width"])
    bh = float(box["height"])
    if viewport_css_width <= 0 or viewport_css_height <= 0:
        return (bx, by, bx + bw, by + bh)
    ix = float(image_width_px) / float(viewport_css_width)
    iy = float(image_height_px) / float(viewport_css_height)
    x1 = bx * ix
    y1 = by * iy
    x2 = (bx + bw) * ix
    y2 = (by + bh) * iy
    return (x1, y1, x2, y2)


def _click_in_bbox_xyxy(
    x1: float, y1: float, x2: float, y2: float, *, mode: Literal["center", "left"]
) -> tuple[float, float]:
    w = max(0.0, x2 - x1)
    h = max(0.0, y2 - y1)
    mid_y = (y1 + y2) / 2.0
    if mode == "center":
        return ((x1 + x2) / 2.0, mid_y)
    cx = x1 + max(4.0, min(w * 0.18, w * 0.35))
    return (cx, mid_y)


def _norm_name(raw: str) -> str:
    return (raw or "").strip().lower().replace(" ", "_")


def suggest_click_heuristic_iframe(
    iframe_box_css: dict[str, float],
    *,
    viewport_css_width: int,
    viewport_css_height: int,
    image_rgb: np.ndarray,
) -> VisionClickResult:
    """
    Heurística: bbox del iframe proyectado a la imagen y clic en zona izquierda.
    No usa YOLO; sirve como baseline o tests del pipeline de coordenadas.
    """
    h, w = int(image_rgb.shape[0]), int(image_rgb.shape[1])
    bbox_img = bbox_css_to_bbox_image(
        iframe_box_css,
        viewport_css_width=float(viewport_css_width),
        viewport_css_height=float(viewport_css_height),
        image_width_px=w,
        image_height_px=h,
    )
    x1, y1, x2, y2 = bbox_img
    cx_i, cy_i = _click_in_bbox_xyxy(x1, y1, x2, y2, mode="left")
    cx_p, cy_p = image_xy_to_page_xy(
        cx_i,
        cy_i,
        viewport_css_width=float(viewport_css_width),
        viewport_css_height=float(viewport_css_height),
        image_width_px=w,
        image_height_px=h,
    )
    return VisionClickResult(
        bbox_image=bbox_img,
        click_image=(cx_i, cy_i),
        click_page=(cx_p, cy_p),
        confidence=1.0,
        class_name="none",
        should_click=True,
    )


def _classify_detection_name(names: dict[int, str], cls_id: int) -> str:
    raw = names.get(int(cls_id), str(int(cls_id)))
    key = _norm_name(str(raw))
    for canonical in (CLS_TARGET, CLS_WIDGET, CLS_SUCCESS):
        if key == _norm_name(canonical):
            return canonical
    return key


class YoloTurnstileDetector:
    """Carga el archivo ``.pt`` una vez y sugiere clic según la política del plan."""

    def __init__(self, weights_path: Path) -> None:
        from ultralytics import YOLO  # noqa: PLC0415

        self._weights = Path(weights_path)
        self._model = YOLO(str(self._weights))

    @property
    def names(self) -> dict[int, str]:
        return dict(self._model.names)

    def suggest(
        self,
        image_rgb: np.ndarray,
        *,
        viewport_css_width: int,
        viewport_css_height: int,
        conf_min: float = 0.4,
        imgsz: int = 640,
    ) -> VisionClickResult:
        """
        Política: ``target_checkbox`` > ``widget_container``; ``success_mark`` no clic.
        Si solo hay ``success_mark`` (sin las otras dos), ``should_click=False``.
        """
        if image_rgb.ndim != 3 or image_rgb.shape[2] != 3:
            raise ValueError("image_rgb debe ser (H, W, 3) RGB uint8")

        h, w = int(image_rgb.shape[0]), int(image_rgb.shape[1])
        image_bgr = np.ascontiguousarray(image_rgb[:, :, ::-1])

        results: list[Any] = self._model.predict(
            source=image_bgr,
            conf=float(conf_min),
            imgsz=int(imgsz),
            verbose=False,
        )
        dets: list[tuple[str, float, tuple[float, float, float, float]]] = []
        if results and results[0].boxes is not None and len(results[0].boxes):
            boxes = results[0].boxes
            xyxy = boxes.xyxy.cpu().numpy()
            confs = boxes.conf.cpu().numpy()
            clss = boxes.cls.cpu().numpy().astype(int)
            names = self.names
            for i in range(len(boxes)):
                cls_id = int(clss[i])
                label = _classify_detection_name(names, cls_id)
                conf = float(confs[i])
                x1, y1, x2, y2 = (
                    float(xyxy[i][0]),
                    float(xyxy[i][1]),
                    float(xyxy[i][2]),
                    float(xyxy[i][3]),
                )
                dets.append((label, conf, (x1, y1, x2, y2)))

        def best_of(label: str) -> tuple[float, tuple[float, float, float, float]] | None:
            cand = [(c, b) for lab, c, b in dets if lab == label]
            if not cand:
                return None
            cand.sort(key=lambda t: t[0], reverse=True)
            return cand[0]

        tgt = best_of(CLS_TARGET)
        wid = best_of(CLS_WIDGET)
        succ = best_of(CLS_SUCCESS)

        if tgt is not None:
            conf, bb = tgt
            x1, y1, x2, y2 = bb
            cx_i, cy_i = _click_in_bbox_xyxy(x1, y1, x2, y2, mode="center")
            cx_p, cy_p = image_xy_to_page_xy(
                cx_i,
                cy_i,
                viewport_css_width=float(viewport_css_width),
                viewport_css_height=float(viewport_css_height),
                image_width_px=w,
                image_height_px=h,
            )
            return VisionClickResult(
                bbox_image=bb,
                click_image=(cx_i, cy_i),
                click_page=(cx_p, cy_p),
                confidence=conf,
                class_name="target_checkbox",
                should_click=True,
            )

        if wid is not None:
            conf, bb = wid
            x1, y1, x2, y2 = bb
            cx_i, cy_i = _click_in_bbox_xyxy(x1, y1, x2, y2, mode="left")
            cx_p, cy_p = image_xy_to_page_xy(
                cx_i,
                cy_i,
                viewport_css_width=float(viewport_css_width),
                viewport_css_height=float(viewport_css_height),
                image_width_px=w,
                image_height_px=h,
            )
            return VisionClickResult(
                bbox_image=bb,
                click_image=(cx_i, cy_i),
                click_page=(cx_p, cy_p),
                confidence=conf,
                class_name="widget_container",
                should_click=True,
            )

        if succ is not None and tgt is None and wid is None:
            conf, bb = succ
            return VisionClickResult(
                bbox_image=bb,
                click_image=None,
                click_page=None,
                confidence=conf,
                class_name="success_mark",
                should_click=False,
            )

        return VisionClickResult(
            bbox_image=None,
            click_image=None,
            click_page=None,
            confidence=0.0,
            class_name="none",
            should_click=False,
        )


def suggest_click_from_image(
    image_rgb: np.ndarray,
    *,
    strategy: Strategy,
    yolo_detector: YoloTurnstileDetector | None,
    iframe_box_css: dict[str, float] | None,
    viewport_css_width: int,
    viewport_css_height: int,
    conf_min: float = 0.4,
) -> VisionClickResult:
    """
    API unificada: ``heuristic_iframe`` requiere ``iframe_box_css``;
    ``yolo`` requiere ``yolo_detector`` (cargar una sola vez en el proceso).
    """
    if strategy == "heuristic_iframe":
        if iframe_box_css is None:
            raise ValueError("heuristic_iframe requiere iframe_box_css")
        return suggest_click_heuristic_iframe(
            iframe_box_css,
            viewport_css_width=viewport_css_width,
            viewport_css_height=viewport_css_height,
            image_rgb=image_rgb,
        )
    if strategy == "yolo":
        if yolo_detector is None:
            raise ValueError("yolo requiere yolo_detector")
        return yolo_detector.suggest(
            image_rgb,
            viewport_css_width=viewport_css_width,
            viewport_css_height=viewport_css_height,
            conf_min=conf_min,
        )
    raise ValueError(f"strategy desconocida: {strategy!r}")


def load_yolo_detector(weights_path: Path) -> YoloTurnstileDetector:
    """Carga el detector YOLO; ``ImportError`` si faltan dependencias de instalación."""
    p = Path(weights_path)
    if not p.is_file():
        raise FileNotFoundError(f"No existe el archivo de pesos YOLO: {p}")
    try:
        return YoloTurnstileDetector(p)
    except ImportError as e:
        raise ImportError(
            "Instala dependencias: pip install camoufox-turnstile "
            "(y torch según tu plataforma)."
        ) from e
