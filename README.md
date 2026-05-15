# camoufox-turnstile

![imagen](docs/images/image1.png)



SDK en Python para integrar **Cloudflare Turnstile** en scrapers o automatizaciones que usen **Camoufox** y **Playwright (async API)** con **inferencia YOLO** (Ultralytics + OpenCV) en todas las rutas principales (`solve_on_page`). Opcionalmente puede activarse **fallback DOM** sobre el iframe cuando no hay una sugerencia YOLO clara (`SolveOptions.use_dom_fallback`).

**v0.2.0:** las dependencias de visión van en el paquete base; el extra `[yolo]` queda vacío (deprecated, no-op) para no romper instalaciones antiguas.

- **YOLO (estándar):** bucle de captura + inferencia con polling, distinción de `success_mark` / `target_checkbox` / `widget_container`, y espera del token en `input[name="cf-turnstile-response"]`.
- **Fallback DOM (dentro del bucle YOLO):** clics heurísticos cuando la detección devuelve `none` y `use_dom_fallback=True` (por defecto).

**Alcance:** sitios que usan el campo oculto estándar `cf-turnstile-response`. No sustituye otros captchas (reCAPTCHA, hCaptcha, etc.).

Para probar el SDK puedes usar el **Turnstile Lab** público: [https://turnstile-lab.builker.com/](https://turnstile-lab.builker.com/) (es la URL por defecto del ejemplo `examples/minimal.py`).

**Guía paso a paso para integrarlo en cualquier proyecto Python:** [INTEGRACION.md](https://github.com/builker-col/turnstile-camoufox-sdk/blob/main/INTEGRACION.md) (enlace absoluto para lectura desde [PyPI](https://pypi.org/project/camoufox-turnstile/)).

```bash
pip install camoufox-turnstile
# bucket S3 privado para pesos (opcional):
pip install 'camoufox-turnstile[s3]'
```

**El archivo `.pt` no va en el wheel de PyPI** y suele obtenerse solo en la primera ejecución: sin `yolo_weights` en `SolveOptions` ni variable `TURNSTILE_YOLO_WEIGHTS`, el SDK puede **descargar** `turnstile-yolo-latest.pt` desde Builker Open Models, guardarlo en caché y reutilizarlo después.

**(torch)** llega habitualmente como dependencia transitiva de Ultralytics; elige la variante CPU/CUDA según tu entorno si la predeterminada no te vale.

Instala también **Camoufox** y ejecuta (una vez por máquina):

```bash
camoufox fetch
```

## Pesos `.pt` (descarga automática por defecto)

El wheel **no** incluye el modelo en PyPI, pero **no tienes que bajarlo tú**: salvo que fijes una ruta local, el SDK lo obtiene de red la primera vez y lo deja en caché.

Prioridad (`ensure_yolo_weights` / `SolveOptions.yolo_weights`):

1. Ruta local explícita (`yolo_weights` en `SolveOptions` o variable `TURNSTILE_YOLO_WEIGHTS`).
2. Archivo en **caché** (`platformdirs`, nombre por defecto **`turnstile-yolo-latest.pt`**).
3. Descarga: **`TURNSTILE_YOLO_WEIGHTS_URL`** o **`TURNSTILE_YOLO_S3_URI`** si las defines; si no, el SDK usa por defecto la última versión pública en Builker Open Models:

   `https://builker-open-models.s3.us-east-2.amazonaws.com/camoufox-turnstile-sdk/turnstile-yolo-latest.pt`

   (constante `DEFAULT_YOLO_WEIGHTS_URL` en el paquete).

Para un bucket **privado** (`s3://bucket/key`) usa `TURNSTILE_YOLO_S3_URI` e instala `pip install 'camoufox-turnstile[s3]'` (boto3 + credenciales en el entorno).

Opcional: **`TURNSTILE_YOLO_WEIGHTS_SHA256`** para verificar integridad tras descarga.  
Opcional: **`TURNSTILE_YOLO_FORCE_DOWNLOAD`** (`1` / `true` / `yes` / `on`): ignora caché y vuelve a bajar el `.pt` (misma URL en S3).  
Opcional: **`TURNSTILE_YOLO_CACHE_BASENAME`** para otro nombre de archivo en caché (p. ej. varias variantes del modelo).

### Sustituiste el `.pt` en S3 con el **mismo** nombre (`turnstile-yolo-latest.pt`)

Los usuarios que ya tengan caché **no** descargan de nuevo solos. Opciones:

- Variable de entorno **`TURNSTILE_YOLO_FORCE_DOWNLOAD=1`** (o `true` / `yes` / `on`) antes de ejecutar, **o**
- En código: `SolveOptions(refresh_yolo_weights=True)`, **o**
- `ensure_yolo_weights(force_download=True)`, **o**
- Borrar el archivo en la caché de usuario (directorio `camoufox_turnstile` / `weights` de `platformdirs`).

### Publicas un modelo con **otra** clave o otra URL

- Puedes fijar **`TURNSTILE_YOLO_WEIGHTS_URL`** (o `TURNSTILE_YOLO_CACHE_BASENAME`) sin subir versión del paquete pip.
- Si quieres que **todos** los installs por defecto apunten a un archivo nuevo, cambia **`DEFAULT_YOLO_WEIGHTS_URL`** en el código del SDK y publica una **nueva versión en PyPI**. El número de versión pip es para **cambios del SDK Python**, no para cada reentrenamiento del modelo si sigues usando env/URL propia.

## Uso rápido

```python
import asyncio
from camoufox.async_api import AsyncCamoufox
from camoufox_turnstile import (
    SolveOptions,
    camoufox_context_options,
    solve_on_page,
    DEFAULT_VIEWPORT,
)

async def main():
    async with AsyncCamoufox(headless=True) as browser:
        ctx = await browser.new_context(
            **camoufox_context_options(viewport=DEFAULT_VIEWPORT)
        )
        page = await ctx.new_page()
        await page.goto("https://turnstile-lab.builker.com/", wait_until="load")
        result = await solve_on_page(page, SolveOptions())
        print(result.visual_ok_via, len(result.token))
        await ctx.close()

asyncio.run(main())
```

**API relevante:** `read_turnstile_token`, `wait_turnstile_token`, `assist_turnstile_clicks`, `assist_turnstile_vision_clicks`, `load_yolo_detector`, `ensure_yolo_weights`.

## Ejemplo en línea de comandos

Desde la raíz del repo del SDK (con entorno editable):

```bash
pip install -e ".[dev]"
python examples/minimal.py --headless
# URL explícita (por defecto ya es el lab público):
python examples/minimal.py "https://turnstile-lab.builker.com/" --headless
```

Pruebas recomendadas contra el **Turnstile Lab** público: https://turnstile-lab.builker.com/

## Construir el paquete (mantenedor)

```bash
pip install build
python -m build
```

Comprueba el wheel en un venv limpio con `pip install dist/camoufox_turnstile-*.whl`.

### Publicar en PyPI

1. Comprueba en [pypi.org](https://pypi.org/) que el nombre del proyecto (`camoufox-turnstile`) esté libre y crea el proyecto en tu cuenta.
2. **Trusted Publishing (recomendado):** en la configuración del proyecto en PyPI, añade un *Trusted Publisher* que apunte a este repositorio y al workflow [`.github/workflows/publish-pypi.yml`](https://github.com/builker-col/turnstile-camoufox-sdk/blob/main/.github/workflows/publish-pypi.yml) **antes** del primer envío por CI. Documentación: [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/) y [Publishing with a trusted publisher](https://docs.pypi.org/trusted-publishers/publishing/).
3. Sube la versión en `pyproject.toml` y crea un tag semántico en Git, p. ej. `git tag v0.2.0 && git push origin v0.2.0`. El workflow construye el paquete y lo publica con OIDC (sin contraseña en el repo).
4. **Alternativa manual:** tras `python -m build`, sube con `twine upload dist/*` y un [API token de PyPI](https://pypi.org/help/#apitoken) (no commitear secretos). Guía PyPA: [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

Tras publicar, verifica en un venv limpio: `pip install camoufox-turnstile` y `python -c "import camoufox_turnstile; print(camoufox_turnstile.__version__)"`.

## Legal y responsabilidad

Respeta los términos de uso del sitio objetivo y la legislación aplicable. Este SDK es una herramienta técnica; el uso indebido es responsabilidad del integrador.

## Enlace al laboratorio

Proyecto de referencia (experimento): repositorio **turnstile-security-lab** (`experiments/camoufox_yolo_turnstile`).

Repositorio del SDK: https://github.com/builker-col/turnstile-camoufox-sdk
