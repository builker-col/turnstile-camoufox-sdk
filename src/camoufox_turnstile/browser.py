"""Camoufox + opciones de contexto Playwright alineadas con visión YOLO."""

from __future__ import annotations

from typing import Any

from camoufox.async_api import AsyncCamoufox

DEFAULT_VIEWPORT: dict[str, int] = {"width": 1366, "height": 960}


def camoufox_context_options(
    *,
    viewport: dict[str, int] | None = None,
    use_yolo: bool,
) -> dict[str, Any]:
    """
    Opciones para ``browser.new_context(...)``.

    Con YOLO fuerza ``device_scale_factor=1`` para alinear captura y viewport CSS.
    """
    vp = dict(viewport or DEFAULT_VIEWPORT)
    opts: dict[str, Any] = {"viewport": vp}
    if use_yolo:
        opts["device_scale_factor"] = 1
    return opts


__all__ = ["AsyncCamoufox", "DEFAULT_VIEWPORT", "camoufox_context_options"]
