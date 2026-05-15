"""Descarga y caché local de pesos YOLO (.pt) desde HTTPS o S3."""

from __future__ import annotations

import hashlib
import logging
import os
import re
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

from platformdirs import user_cache_dir

log = logging.getLogger(__name__)

# Última versión publicada (mismo key en S3; descarga por HTTPS sin credenciales).
DEFAULT_YOLO_WEIGHTS_URL = (
    "https://builker-open-models.s3.us-east-2.amazonaws.com/"
    "camoufox-turnstile-sdk/turnstile-yolo-latest.pt"
)
DEFAULT_YOLO_CACHE_BASENAME = "turnstile-yolo-latest.pt"

ENV_LOCAL = "TURNSTILE_YOLO_WEIGHTS"
ENV_URL = "TURNSTILE_YOLO_WEIGHTS_URL"
ENV_S3 = "TURNSTILE_YOLO_S3_URI"
ENV_SHA256 = "TURNSTILE_YOLO_WEIGHTS_SHA256"
ENV_CACHE_BASENAME = "TURNSTILE_YOLO_CACHE_BASENAME"
ENV_FORCE_DOWNLOAD = "TURNSTILE_YOLO_FORCE_DOWNLOAD"

_MIN_BYTES = 512 * 1024


def _env_truthy(name: str) -> bool:
    v = (os.environ.get(name) or "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _default_cache_path(basename: str) -> Path:
    base = user_cache_dir("camoufox_turnstile", appauthor=False)
    d = Path(base) / "weights"
    d.mkdir(parents=True, exist_ok=True)
    return d / basename


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _verify_sha256(path: Path, expected: str) -> bool:
    got = _sha256_file(path).lower()
    return got == expected.strip().lower()


def _download_https(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "camoufox-turnstile/0.1 (+https://pypi.org/project/camoufox-turnstile/)"},
        )
        # Modelos .pt pueden ser grandes; streaming evita cargar todo en RAM.
        with urllib.request.urlopen(req, timeout=600) as resp:  # noqa: S310
            with tmp.open("wb") as f:
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
        tmp.replace(dest)
    except (urllib.error.URLError, OSError):
        if tmp.is_file():
            tmp.unlink(missing_ok=True)
        raise


def _download_s3(uri: str, dest: Path) -> None:
    m = re.match(r"^s3://([^/]+)/(.+)$", uri.strip())
    if not m:
        raise ValueError(f"S3 URI inválida (esperado s3://bucket/key): {uri!r}")
    bucket, key = m.group(1), m.group(2)
    try:
        import boto3  # type: ignore[import-untyped]
    except ImportError as e:
        raise ImportError(
            "Para s3:// instala boto3: pip install 'camoufox-turnstile[s3]'"
        ) from e
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        client = boto3.client("s3")
        client.download_file(bucket, key, str(tmp))
        tmp.replace(dest)
    except Exception:
        if tmp.is_file():
            tmp.unlink(missing_ok=True)
        raise


def ensure_yolo_weights(
    *,
    local_path: str | Path | None = None,
    weights_url: str | None = None,
    s3_uri: str | None = None,
    expected_sha256: str | None = None,
    cache_basename: str | None = None,
    force_download: bool = False,
) -> Path:
    """
    Resuelve la ruta a un archivo ``.pt`` local.

    **Descarga automática (sin pasos manuales):** si no pasas ``local_path`` ni
    defines ``TURNSTILE_YOLO_WEIGHTS``, el SDK usa la caché de usuario o **baja
    solo** el modelo desde la URL pública por defecto
    (``DEFAULT_YOLO_WEIGHTS_URL``, archivo ``turnstile-yolo-latest.pt``). Las
    siguientes ejecuciones reutilizan el archivo en disco.

    Prioridad: ``local_path`` → ``TURNSTILE_YOLO_WEIGHTS`` → caché válida →
    descarga vía ``weights_url`` / ``TURNSTILE_YOLO_WEIGHTS_URL`` /
    ``TURNSTILE_YOLO_S3_URI`` / URL pública por defecto.

    Si ``TURNSTILE_YOLO_FORCE_DOWNLOAD`` es verdadera (``1``, ``true``, …) o
    pasas ``force_download=True``, se ignora la caché y se vuelve a descargar
    (útil cuando sustituyes el objeto en S3 con el mismo nombre de clave).
    """
    force_download = bool(force_download) or _env_truthy(ENV_FORCE_DOWNLOAD)

    sha_env = (os.environ.get(ENV_SHA256) or "").strip() or None
    expected_sha256 = expected_sha256 or sha_env

    if local_path is not None:
        p = Path(local_path).expanduser().resolve()
        if not p.is_file():
            raise FileNotFoundError(f"No existe el archivo de pesos: {p}")
        if expected_sha256 and not _verify_sha256(p, expected_sha256):
            raise ValueError("El archivo local no coincide con TURNSTILE_YOLO_WEIGHTS_SHA256")
        return p

    env_local = (os.environ.get(ENV_LOCAL) or "").strip()
    if env_local:
        p = Path(env_local).expanduser().resolve()
        if not p.is_file():
            raise FileNotFoundError(
                f"{ENV_LOCAL} apunta a un archivo inexistente: {p}"
            )
        if expected_sha256 and not _verify_sha256(p, expected_sha256):
            raise ValueError("El archivo local no coincide con el SHA256 configurado")
        return p

    url = (weights_url or os.environ.get(ENV_URL) or "").strip() or None
    s3 = (s3_uri or os.environ.get(ENV_S3) or "").strip() or None
    if not url and not s3:
        url = DEFAULT_YOLO_WEIGHTS_URL

    basename = (
        cache_basename
        or (os.environ.get(ENV_CACHE_BASENAME) or "").strip()
        or DEFAULT_YOLO_CACHE_BASENAME
    )
    cache_path = _default_cache_path(basename)

    if (
        not force_download
        and cache_path.is_file()
        and cache_path.stat().st_size >= _MIN_BYTES
    ):
        if expected_sha256:
            if _verify_sha256(cache_path, expected_sha256):
                log.info("Usando pesos YOLO en caché (SHA256 OK): %s", cache_path)
                return cache_path
            log.warning("Caché con SHA256 incorrecto; se vuelve a descargar.")
        else:
            log.info("Usando pesos YOLO en caché (sin verificación SHA256): %s", cache_path)
            return cache_path

    log.info(
        "Descarga automática del modelo YOLO (primera vez o sin caché válida) → %s",
        cache_path,
    )
    with tempfile.TemporaryDirectory(dir=cache_path.parent) as td:
        tmp_dest = Path(td) / "download.pt"
        if url:
            log.info("Descargando pesos YOLO por HTTPS (%s)…", url[:80] + ("…" if len(url) > 80 else ""))
            _download_https(url, tmp_dest)
        else:
            assert s3 is not None
            log.info("Descargando pesos YOLO desde S3…")
            _download_s3(s3, tmp_dest)
        if tmp_dest.stat().st_size < _MIN_BYTES:
            raise ValueError("Descarga demasiado pequeña; comprobar URL o credenciales S3.")
        if expected_sha256 and not _verify_sha256(tmp_dest, expected_sha256):
            raise ValueError(
                "SHA256 de la descarga no coincide con TURNSTILE_YOLO_WEIGHTS_SHA256"
            )
        tmp_dest.replace(cache_path)

    log.info("Modelo YOLO listo en: %s", cache_path)
    return cache_path
