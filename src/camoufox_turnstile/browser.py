"""Camoufox + opciones de contexto Playwright alineadas con visión YOLO."""

from __future__ import annotations

from typing import Any

from camoufox.async_api import AsyncCamoufox

DEFAULT_VIEWPORT: dict[str, int] = {"width": 1366, "height": 960}


def camoufox_context_options(
    *,
    viewport: dict[str, int] | None = None,
) -> dict[str, Any]:
    """
    Opciones para ``browser.new_context(...)``.

    Fuerza ``device_scale_factor=1`` para alinear captura PNG y viewport CSS con
    el bucle YOLO.
    """
    vp = dict(viewport or DEFAULT_VIEWPORT)
    return {"viewport": vp, "device_scale_factor": 1}


__all__ = ["AsyncCamoufox", "DEFAULT_VIEWPORT", "camoufox_context_options"]
