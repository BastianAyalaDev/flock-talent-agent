from __future__ import annotations

from rag.pipeline import Answer
from rag.retrieval import RetrievedChunk
from rag.ui_helpers import (
    append_message,
    index_ready,
    is_blank,
    submit_question,
    to_llm_history,
)


def _rc(source="proceso.md", section="A > B"):
    return RetrievedChunk(text="t", source=source, section=section, distance=0.1)


def test_is_blank():
    assert is_blank("") and is_blank("   \n\t") and is_blank(None)
    assert not is_blank(" hola ")


def test_append_message_ignora_vacios():
    h = []
    assert append_message(h, "user", "   ") is False
    assert h == []


def test_append_message_guarda_en_orden_sin_fuentes():
    h = []
    append_message(h, "user", "hola")
    assert append_message(h, "assistant", "chau") is True
    assert [m["role"] for m in h] == ["user", "assistant"]
    assert all("sources" not in m for m in h)


def test_to_llm_history_solo_role_y_content():
    h = [{"role": "user", "content": "hola", "extra": 1}]
    assert to_llm_history(h) == [{"role": "user", "content": "hola"}]


def test_submit_question_vacia_no_llama_al_pipeline():
    calls = []
    h = []
    assert submit_question(h, "  ", lambda q, hist: calls.append(q)) is False
    assert calls == [] and h == []


def test_submit_question_agrega_turno_y_pasa_historial_previo():
    h = []
    append_message(h, "user", "u0")
    append_message(h, "assistant", "a0")
    seen = {}

    def fn(q, hist):
        seen["q"], seen["hist"] = q, hist
        return Answer(text="resp", sources=[_rc()])

    assert submit_question(h, "  nueva  ", fn) is True
    assert seen["q"] == "nueva"
    assert seen["hist"] == [
        {"role": "user", "content": "u0"},
        {"role": "assistant", "content": "a0"},
    ]
    assert [m["content"] for m in h] == ["u0", "a0", "nueva", "resp"]
    assert "sources" not in h[-1]


class _Col:
    def __init__(self, n=None, error=None):
        self.n, self.error = n, error

    def count(self):
        if self.error:
            raise self.error
        return self.n


def test_index_ready():
    assert index_ready(_Col(5)) is True
    assert index_ready(_Col(0)) is False
    assert index_ready(None) is False
    assert index_ready(_Col(error=RuntimeError("x"))) is False
