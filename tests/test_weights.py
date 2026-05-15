"""Tests del resolver de pesos (sin YOLO ni red real)."""

from __future__ import annotations

from pathlib import Path

import pytest

import camoufox_turnstile.weights as weights_mod
from camoufox_turnstile.weights import ensure_yolo_weights


def test_ensure_weights_local(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = tmp_path / "w.pt"
    p.write_bytes(b"x" * (600 * 1024))
    monkeypatch.delenv("TURNSTILE_YOLO_WEIGHTS", raising=False)
    monkeypatch.delenv("TURNSTILE_YOLO_WEIGHTS_URL", raising=False)
    monkeypatch.delenv("TURNSTILE_YOLO_S3_URI", raising=False)
    monkeypatch.delenv("TURNSTILE_YOLO_FORCE_DOWNLOAD", raising=False)
    out = ensure_yolo_weights(local_path=p)
    assert out == p.resolve()


def test_ensure_weights_default_https(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for key in (
        "TURNSTILE_YOLO_WEIGHTS",
        "TURNSTILE_YOLO_WEIGHTS_URL",
        "TURNSTILE_YOLO_S3_URI",
        "TURNSTILE_YOLO_WEIGHTS_SHA256",
        "TURNSTILE_YOLO_FORCE_DOWNLOAD",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr(
        weights_mod,
        "user_cache_dir",
        lambda *args, **kwargs: str(tmp_path),
    )

    def fake_download(url: str, dest: Path) -> None:
        assert url == weights_mod.DEFAULT_YOLO_WEIGHTS_URL
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"x" * (600 * 1024))

    monkeypatch.setattr(weights_mod, "_download_https", fake_download)
    out = ensure_yolo_weights(force_download=True)
    assert out.name == weights_mod.DEFAULT_YOLO_CACHE_BASENAME
    assert out.is_file()


def test_force_download_env_redownloads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for key in (
        "TURNSTILE_YOLO_WEIGHTS",
        "TURNSTILE_YOLO_WEIGHTS_URL",
        "TURNSTILE_YOLO_S3_URI",
        "TURNSTILE_YOLO_WEIGHTS_SHA256",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.delenv("TURNSTILE_YOLO_FORCE_DOWNLOAD", raising=False)
    monkeypatch.setattr(
        weights_mod,
        "user_cache_dir",
        lambda *args, **kwargs: str(tmp_path),
    )
    calls = {"n": 0}

    def fake_download(url: str, dest: Path) -> None:
        calls["n"] += 1
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"x" * (600 * 1024))

    monkeypatch.setattr(weights_mod, "_download_https", fake_download)
    ensure_yolo_weights()
    assert calls["n"] == 1
    ensure_yolo_weights()
    assert calls["n"] == 1
    monkeypatch.setenv("TURNSTILE_YOLO_FORCE_DOWNLOAD", "1")
    ensure_yolo_weights()
    assert calls["n"] == 2
