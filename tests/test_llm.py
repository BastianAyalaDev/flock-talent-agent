from __future__ import annotations

from types import SimpleNamespace

import httpx
import openai
import pytest

from rag import llm as llm_module
from rag.llm import LLMError, make_llm

MSGS = [{"role": "user", "content": "hola"}]


def _request():
    return httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")


def _status_error(cls, code):
    return cls("boom", response=httpx.Response(code, request=_request()), body=None)


class FakeClient:
    def __init__(self, content=None, error=None, empty_choices=False):
        self.calls = []
        self._content = content
        self._error = error
        self._empty = empty_choices
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        if self._error is not None:
            raise self._error
        if self._empty:
            return SimpleNamespace(choices=[])
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self._content))]
        )


def test_usa_el_modelo_dado_y_devuelve_el_texto():
    client = FakeClient(content="Respuesta")
    llm = make_llm("k", "modelo/x:free", client=client)
    assert llm(MSGS) == "Respuesta"
    assert client.calls[0]["model"] == "modelo/x:free"
    assert client.calls[0]["messages"] == MSGS


@pytest.mark.parametrize(
    "error,fragment",
    [
        (_status_error(openai.RateLimitError, 429), "saturado"),
        (_status_error(openai.AuthenticationError, 401), "API key"),
        (openai.APIConnectionError(request=_request()), "No pude contactar"),
        (openai.APITimeoutError(request=_request()), "No pude contactar"),
        (_status_error(openai.APIStatusError, 500), "No pude contactar"),
    ],
)
def test_errores_de_openai_se_traducen_a_llmerror(error, fragment):
    llm = make_llm("k", "m", client=FakeClient(error=error))
    with pytest.raises(LLMError) as exc:
        llm(MSGS)
    assert fragment in str(exc.value)


@pytest.mark.parametrize("content", [None, "", "   "])
def test_respuesta_vacia_es_llmerror(content):
    llm = make_llm("k", "m", client=FakeClient(content=content))
    with pytest.raises(LLMError, match="No pude contactar"):
        llm(MSGS)


def test_sin_choices_es_llmerror():
    llm = make_llm("k", "m", client=FakeClient(empty_choices=True))
    with pytest.raises(LLMError, match="No pude contactar"):
        llm(MSGS)


def test_sin_client_construye_openai_apuntando_a_openrouter(monkeypatch):
    captured = {}

    class FakeOpenAI(FakeClient):
        def __init__(self, **kwargs):
            captured.update(kwargs)
            super().__init__(content="ok")

    monkeypatch.setattr(llm_module, "OpenAI", FakeOpenAI)
    llm = make_llm("secreta", "m")
    assert captured["base_url"] == "https://openrouter.ai/api/v1"
    assert captured["api_key"] == "secreta"
    assert llm(MSGS) == "ok"
