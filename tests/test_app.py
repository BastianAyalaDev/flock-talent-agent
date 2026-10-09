"""Tests de la UI con streamlit.testing.v1.AppTest (offline, sin LLM ni modelos)."""
from __future__ import annotations

import os

import pytest
from streamlit.testing.v1 import AppTest

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")


@pytest.fixture(autouse=True)
def _env_aislado(monkeypatch, tmp_path):
    # El entorno real gana sobre .env (override=False): fijar los valores aisla de un .env real.
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    monkeypatch.setenv("OPENROUTER_MODEL", "")
    monkeypatch.setenv("TOP_K", "")
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "sin_indice"))


def _run():
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    return at


def test_sin_api_key_muestra_error_sin_excepcion():
    at = _run()

    assert not at.exception
    assert len(at.error) == 1
    assert "OPENROUTER_API_KEY" in at.error[0].value
    assert len(at.chat_input) == 0


def test_con_key_y_sin_indice_avisa_que_hay_que_ingestar(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "dummy-key")

    at = _run()

    assert not at.exception
    assert len(at.error) == 0
    assert len(at.warning) == 1
    assert "python ingest.py" in at.warning[0].value
    assert len(at.chat_input) == 0
