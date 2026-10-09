from __future__ import annotations

from rag.llm import LLMError
from rag.pipeline import Answer, answer, strip_citations
from rag.prompting import NO_SE


class FakeCollection:
    def __init__(self, rows):
        self.rows = rows

    def query(self, query_texts, n_results, **kwargs):
        rows = self.rows[:n_results]
        return {
            "documents": [[r[0] for r in rows]],
            "metadatas": [[r[1] for r in rows]],
            "distances": [[r[2] for r in rows]],
        }


def _col():
    return FakeCollection(
        [
            ("t1", {"source": "proceso.md", "section": "A > B"}, 0.1),
            ("t2", {"source": "proceso.md", "section": "A > C"}, 0.2),
        ]
    )


def test_devuelve_texto_y_fuentes():
    res = answer("¿qué?", [], _col(), lambda m: "Respuesta", k=4, max_turns=3)
    assert isinstance(res, Answer)
    assert res.text == "Respuesta"
    assert [(s.source, s.section) for s in res.sources] == [
        ("proceso.md", "A > B"),
        ("proceso.md", "A > C"),
    ]


def test_fuentes_sin_duplicados():
    col = FakeCollection(
        [
            ("t1", {"source": "p.md", "section": "A"}, 0.1),
            ("t2", {"source": "p.md", "section": "A"}, 0.2),
            ("t3", {"source": "p.md", "section": "B"}, 0.3),
        ]
    )
    res = answer("q", [], col, lambda m: "ok", k=4, max_turns=3)
    assert [s.section for s in res.sources] == ["A", "B"]


def test_prompt_enviado_contiene_regla_no_se_y_la_pregunta():
    seen = {}

    def llm(msgs):
        seen["msgs"] = msgs
        return NO_SE

    res = answer("capital de Francia", [], FakeCollection([]), llm, k=4, max_turns=3)
    assert res.text == NO_SE
    assert res.sources == []
    assert NO_SE in seen["msgs"][0]["content"]
    assert "capital de Francia" in seen["msgs"][-1]["content"]


def test_llmerror_devuelve_mensaje_amigable_sin_fuentes():
    def llm(msgs):
        raise LLMError("El modelo gratuito está saturado, probá en unos segundos.")

    res = answer("q", [], _col(), llm, k=4, max_turns=3)
    assert res.text == "El modelo gratuito está saturado, probá en unos segundos."
    assert res.sources == []


def test_historial_se_recorta():
    history = []
    for i in range(10):
        history.append({"role": "user", "content": "u%d" % i})
        history.append({"role": "assistant", "content": "a%d" % i, "sources": ["x"]})
    seen = {}

    def llm(msgs):
        seen["msgs"] = msgs
        return "ok"

    answer("q", history, _col(), llm, k=4, max_turns=3)
    # system + 6 de historial + pregunta final
    assert len(seen["msgs"]) == 8
    assert seen["msgs"][1]["content"] == "u7"
    assert all(set(m) == {"role", "content"} for m in seen["msgs"])


def test_strip_citations_quita_marcadores():
    assert strip_citations("Es así [1].") == "Es así."
    assert strip_citations("Es así [2, 3] y más [1][2].") == "Es así y más."
    assert strip_citations("Ver [1,2,3], listo") == "Ver, listo"
    assert strip_citations("Sin marcadores") == "Sin marcadores"
    assert strip_citations("Lista [x] queda") == "Lista [x] queda"
    assert strip_citations("a\n- uno [4]\n- dos") == "a\n- uno\n- dos"


def test_answer_limpia_citas_residuales_del_llm():
    res = answer("q", [], _col(), lambda m: "Respuesta [1] clara [2, 3].", k=4, max_turns=3)
    assert res.text == "Respuesta clara."


def test_app_no_renderiza_fuentes():
    import os
    app = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
    src = open(app, encoding="utf-8").read()
    assert "Fuentes" not in src and "format_sources" not in src
