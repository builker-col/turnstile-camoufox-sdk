# Integrar `camoufox-turnstile` en cualquier proyecto Python

Esta guía explica cómo añadir el SDK a un proyecto **existente** (CLI, scraper, worker, API, etc.) que use Python **3.10+**. El paquete se instala con **pip** como cualquier otra dependencia; el flujo de automatización es **asíncrono** (igual que Playwright async).

---

## 1. Requisitos

| Requisito | Notas |
|------------|--------|
| Python | 3.10 o superior |
| Sistema | Donde puedas ejecutar **Camoufox** (Firefox embebido) |
| Red | La primera ejecución de `solve_on_page` puede **descargar solo** el `.pt`; luego queda en caché en disco (ver sección 7). |

---

## 2. Añadir la dependencia al proyecto

El wheel incluye **Ultralytics y OpenCV** como dependencias del paquete base (inferencia YOLO siempre disponible sin extras).

```bash
pip install camoufox-turnstile
```

Extras opcionales:

- **`[s3]`**: descarga de pesos desde un bucket AWS privado (`boto3`).

```bash
pip install 'camoufox-turnstile[s3]'
```

> El extra **`[yolo]`** existe vacío solo por compatibilidad con proyectos antiguos; desde **v0.2.0** no añade paquetes adicionales.

### `requirements.txt`

```text
camoufox-turnstile>=0.2.0
```

### `pyproject.toml` (PEP 621)

```toml
[project]
dependencies = [
  "camoufox-turnstile>=0.2.0",
]
```

**Torch:** Ultralytics necesita PyTorch; el SDK no fija el wheel de Torch (CPU vs CUDA). Instala el paquete `torch` que corresponda a tu máquina según la [documentación de PyTorch](https://pytorch.org/get-started/locally/).

---

## 3. Binario Camoufox (una vez por máquina o imagen Docker)

Camoufox no es solo pip: hay que obtener el navegador:

```bash
camoufox fetch
```

En **Docker**, ejecuta esto en la capa de build o en el entrypoint antes de abrir el navegador. Sin esto, `AsyncCamoufox` fallará al arrancar.

---

## 4. Patrón mínimo en código (async)

Flujo típico:

1. Abrir `AsyncCamoufox`.
2. Crear contexto con `camoufox_context_options(...)` (fija `device_scale_factor=1` alineado con las capturas YOLO).
3. `page.goto(...)` a la URL donde está el widget.
4. `await solve_on_page(page, SolveOptions(...))` → obtienes el **token** en `result.token`.

```python
import asyncio
from camoufox.async_api import AsyncCamoufox
from camoufox_turnstile import (
    DEFAULT_VIEWPORT,
    SolveOptions,
    camoufox_context_options,
    solve_on_page,
)

async def obtener_token_turnstile(url: str, *, headless: bool = True) -> str:
    async with AsyncCamoufox(headless=headless) as browser:
        ctx = await browser.new_context(
            **camoufox_context_options(
                viewport=DEFAULT_VIEWPORT,
            )
        )
        page = await ctx.new_page()
        await page.goto(url, wait_until="load")
        result = await solve_on_page(
            page,
            SolveOptions(
                token_timeout_ms=120_000,
                iframe_wait_sec=5.0,
            ),
        )
        await ctx.close()
    return result.token


if __name__ == "__main__":
    token = asyncio.run(
        obtener_token_turnstile("https://turnstile-lab.builker.com/")
    )
    print("longitud del token:", len(token))
```

**Importante:** el sitio debe exponer el token en el input estándar `name="cf-turnstile-response"`. Eso es lo que espera el SDK.

---

## 5. Proyecto “solo síncrono”

Si tu scraper es síncrono, encapsula una sola corrutina y ejecútala con `asyncio.run(...)` (o `asyncio.get_event_loop().run_until_complete` en código legado). No hace falta convertir todo el proyecto a async: basta un **punto de entrada** async donde vivas Camoufox + Playwright.

---

## 6. Ajustar comportamiento (`SolveOptions`)

Ejemplos de campos que suele tocar un integrador:

| Campo | Uso |
|--------|-----|
| `token_timeout_ms` | Tiempo máximo de espera del token (también acota el bucle de polling YOLO). |
| `iframe_wait_sec` | Espera inicial para que monte el iframe antes de asistir. |
| `yolo_weights` | `Path` a un `.pt` local; si es `None`, se usa `ensure_yolo_weights()` (caché + URL por defecto o variables de entorno). |
| `vision_poll_interval_sec` | Pausa entre capturas en el bucle YOLO. |
| `max_yolo_clicks` / `max_dom_attempts` | Límites de interacción para no spamear el widget. |
| `use_dom_fallback` | Si es `False`, no se aplican clics heurísticos sobre el iframe cuando la inferencia devuelve `none`. |
| `refresh_yolo_weights` | `True`: ignora caché del `.pt` y vuelve a descargar (misma URL en S3). |

Lista completa en el código: `camoufox_turnstile.solve.SolveOptions`.

---

## 7. Pesos del modelo: descarga **automática** (cero pasos manuales)

Con `pip install camoufox-turnstile` y **`SolveOptions()` sin `yolo_weights`** (y sin variable `TURNSTILE_YOLO_WEIGHTS`), la primera llamada a `solve_on_page` ejecuta `ensure_yolo_weights()` internamente: **descarga sola** `turnstile-yolo-latest.pt` desde la URL pública de Builker Open Models, la guarda en la caché de usuario (`platformdirs`) y las siguientes ejecuciones **solo leen disco**.

Para **volver a bajar** el mismo nombre de archivo (p. ej. sustituiste el objeto en S3 y la URL no cambió): `TURNSTILE_YOLO_FORCE_DOWNLOAD=1`, o `SolveOptions(refresh_yolo_weights=True)`, o `ensure_yolo_weights(force_download=True)`.

No hace falta `curl`, `wget` ni copiar el archivo al repositorio de tu proyecto.

### ¿Versión en pip?

- **Solo cambias el `.pt` en S3** (misma URL / misma clave): **no** hace falta subir versión nueva del paquete en PyPI; los usuarios que necesiten el binario nuevo fuerzan recarga con lo anterior o borrando caché.
- **Cambias la URL por defecto en el código del SDK** (nuevo `DEFAULT_YOLO_WEIGHTS_URL` o lógica nueva): entonces sí conviene publicar **`camoufox-turnstile` X.Y.Z** en PyPI.

### Sobrescribir el origen (opcional)

Solo si quieres otro origen o un archivo ya descargado:

| Variable / API | Uso |
|----------------|-----|
| `TURNSTILE_YOLO_WEIGHTS` | Ruta a un `.pt` ya presente (sin red). |
| `SolveOptions(yolo_weights=Path(...))` | Igual, desde código. |
| `TURNSTILE_YOLO_WEIGHTS_URL` | Otra URL HTTPS (sustituye el origen por defecto). |
| `TURNSTILE_YOLO_S3_URI` | `s3://bucket/clave` con extra `[s3]` y credenciales AWS. |
| `TURNSTILE_YOLO_WEIGHTS_SHA256` | Comprueba integridad tras descarga. |
| `TURNSTILE_YOLO_FORCE_DOWNLOAD` | `1` / `true` / `yes` / `on`: ignora caché y vuelve a descargar el `.pt`. |

Constantes útiles en el paquete: `DEFAULT_YOLO_WEIGHTS_URL`, `DEFAULT_YOLO_CACHE_BASENAME`.

---

## 8. API de más bajo nivel (control fino)

Si ya tienes un `Page` y solo quieres una parte del flujo:

| Función | Rol |
|---------|-----|
| `read_turnstile_token(page)` | Lee el valor actual del token si ya existe. |
| `wait_turnstile_token(page, timeout_ms=...)` | Espera a que el input tenga valor. |
| `assist_turnstile_clicks` / `assist_turnstile_vision_clicks` | Solo asistencia al widget (sin bucle de polling unificado). |
| `load_yolo_detector` + `YoloTurnstileDetector` | Inferencia YOLO dentro de tu propio bucle si no usas `solve_on_page`. |

Útil si compartes el mismo `BrowserContext` entre muchas URLs y quieres insertar la asistencia en un punto concreto de tu pipeline.

---

## 9. Errores y logging

- **`TurnstileTokenTimeout`**: no apareció token a tiempo (revisa red, claves de sitio, o si la página no usa el input estándar).
- **`TurnstileError`**: base de errores del SDK.
- El SDK usa el **`logging`** de la biblioteca estándar; configura el nivel en tu aplicación (`logging.basicConfig` o dictConfig) para ver mensajes informativos del bucle YOLO/DOM.

**Seguridad:** no registres el token completo en logs ni en issues; basta longitud o prefijo para depurar.

---

## 10. Buenas prácticas

- Reutiliza **un** `AsyncCamoufox` / contexto por lote de URLs si te conviene compartir cookies o perfil.
- Ajusta `headless` según depuración (a veces Turnstile se comporta distinto).
- Respeta los **términos de uso** del sitio y la normativa aplicable; el SDK no “autoriza” un uso concreto.

---

## 11. Página de prueba

Para validar la integración: [https://turnstile-lab.builker.com/](https://turnstile-lab.builker.com/)

En el repositorio del SDK, `examples/minimal.py` usa esa URL por defecto.

---

## Referencias

- README principal del paquete: [README.md](README.md)
- Repositorio: [turnstile-camoufox-sdk](https://github.com/builker-col/turnstile-camoufox-sdk)
