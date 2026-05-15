"""SDK Camoufox + Turnstile con inferencia YOLO (polling) para Playwright async."""

from __future__ import annotations

import importlib
from importlib.metadata import PackageNotFoundError, version

from camoufox_turnstile.assist import (
    assist_turnstile_clicks,
    assist_turnstile_vision_clicks,
    try_click_turnstile_widget,
)
from camoufox_turnstile.browser import (
    DEFAULT_VIEWPORT,
    AsyncCamoufox,
    camoufox_context_options,
)
from camoufox_turnstile.solve import (
    SolveOptions,
    SolveResult,
    TurnstileError,
    TurnstileTokenTimeout,
    read_turnstile_token,
    solve_on_page,
    wait_turnstile_token,
)
from camoufox_turnstile.weights import (
    DEFAULT_YOLO_CACHE_BASENAME,
    DEFAULT_YOLO_WEIGHTS_URL,
    ensure_yolo_weights,
)

_LAZY_VISION = frozenset({
    "VisionClickResult",
    "YoloTurnstileDetector",
    "decode_screenshot_png",
    "load_yolo_detector",
    "suggest_click_from_image",
})

__all__ = [
    "DEFAULT_VIEWPORT",
    "DEFAULT_YOLO_CACHE_BASENAME",
    "DEFAULT_YOLO_WEIGHTS_URL",
    "AsyncCamoufox",
    "VisionClickResult",
    "YoloTurnstileDetector",
    "SolveOptions",
    "SolveResult",
    "TurnstileError",
    "TurnstileTokenTimeout",
    "assist_turnstile_clicks",
    "assist_turnstile_vision_clicks",
    "camoufox_context_options",
    "decode_screenshot_png",
    "ensure_yolo_weights",
    "load_yolo_detector",
    "read_turnstile_token",
    "solve_on_page",
    "suggest_click_from_image",
    "try_click_turnstile_widget",
    "wait_turnstile_token",
]

try:
    __version__ = version("camoufox-turnstile")
except PackageNotFoundError:
    __version__ = "0.0.0"


def __getattr__(name: str):
    if name in _LAZY_VISION:
        mod = importlib.import_module("camoufox_turnstile.vision")
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
