"""
Ejemplo mínimo: abre una URL con Camoufox y resuelve Turnstile con YOLO.

La URL por defecto es el **Turnstile Lab** público de Builker (página dedicada a pruebas):

    https://turnstile-lab.builker.com/

Uso (tras ``camoufox fetch``; los pesos YOLO se resuelven por caché o descarga automática)::

    python examples/minimal.py
    python examples/minimal.py https://turnstile-lab.builker.com/ --headless

Ver README del paquete ``camoufox-turnstile`` para variables de entorno de pesos.
"""

from __future__ import annotations

DEFAULT_LAB_URL = "https://turnstile-lab.builker.com/"

import argparse
import asyncio
import logging
import sys

from camoufox.async_api import AsyncCamoufox

from camoufox_turnstile.browser import DEFAULT_VIEWPORT, camoufox_context_options
from camoufox_turnstile.solve import SolveOptions, solve_on_page

logging.basicConfig(level=logging.INFO)


async def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "url",
        nargs="?",
        default=DEFAULT_LAB_URL,
        help=f"URL con Turnstile (por defecto: {DEFAULT_LAB_URL})",
    )
    p.add_argument("--headless", action="store_true", help="Navegador sin ventana")
    args = p.parse_args()

    async with AsyncCamoufox(headless=args.headless) as browser:
        ctx = await browser.new_context(
            **camoufox_context_options(viewport=DEFAULT_VIEWPORT)
        )
        page = await ctx.new_page()
        await page.goto(args.url, wait_until="load")
        opt = SolveOptions(iframe_wait_sec=4.0, token_timeout_ms=120_000)
        result = await solve_on_page(page, opt)
        print(
            "OK:",
            "len(token)=",
            len(result.token),
            "visual_ok_via=",
            result.visual_ok_via,
            "vision_iterations=",
            result.vision_iterations,
        )
        await ctx.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
