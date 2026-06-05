"""Testes para config.py"""

import pytest


def test_config_constants_types():
    from config import MAX_RETRIES, UPLOAD_TIMEOUT, IMAGE_WIDTH, IMAGE_HEIGHT
    assert isinstance(MAX_RETRIES, int)
    assert isinstance(UPLOAD_TIMEOUT, int)
    assert IMAGE_WIDTH == 1080
    assert IMAGE_HEIGHT == 1080


def test_validate_missing_keys(monkeypatch):
    monkeypatch.setattr("config.GEMINI_API_KEY", "")
    monkeypatch.setattr("config.COMPOSIO_API_KEY", "")
    from config import validate
    with pytest.raises(SystemExit) as exc:
        validate()
    assert exc.value.code == 1


def test_validate_ok(monkeypatch):
    monkeypatch.setattr("config.GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr("config.COMPOSIO_API_KEY", "fake-key")
    from config import validate
    validate()
