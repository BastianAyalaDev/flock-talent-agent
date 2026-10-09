from __future__ import annotations

from rag.retrieval import RetrievedChunk, retrieve


class FakeCollection:
    """Imita la forma de respuesta de chromadb.Collection.query."""

    def __init__(self, n):
        self.rows = [
            ("texto %d" % i, {"source": "proceso.md", "section": "Sec %d" % i}, 0.1 * i)
            for i in range(n)
        ]
        self.calls = []

    def query(self, query_texts, n_results, **kwargs):
        self.calls.append((query_texts, n_results))
        rows = self.rows[:n_results]
        return {
            "ids": [["id%d" % i for i in range(len(rows))]],
            "documents": [[r[0] for r in rows]],
            "metadatas": [[r[1] for r in rows]],
            "distances": [[r[2] for r in rows]],
        }


def test_devuelve_k_resultados_en_orden():
    col = FakeCollection(10)
    res = retrieve(col, "¿qué es el F360?", 3)
    assert len(res) == 3
    assert res[0] == RetrievedChunk(text="texto 0", source="proceso.md", section="Sec 0", distance=0.0)
    assert [r.section for r in res] == ["Sec 0", "Sec 1", "Sec 2"]
    assert res[1].distance < res[2].distance
    assert col.calls == [(["¿qué es el F360?"], 3)]


def test_coleccion_vacia_devuelve_lista_vacia():
    assert retrieve(FakeCollection(0), "hola", 4) == []


def test_respuesta_sin_claves_devuelve_lista_vacia():
    class Raro:
        def query(self, **kw):
            return {"documents": [], "metadatas": [], "distances": []}

    assert retrieve(Raro(), "hola", 4) == []


def test_con_chroma_real_en_memoria(client):
    from rag.chunking import Chunk
    from rag.store import open_collection, rebuild_collection
    from tests.fakes import FakeEmbeddingFunction

    ef = FakeEmbeddingFunction()
    chunks = [Chunk("a.md::%03d" % i, "t%d" % i, "a.md", "S > %d" % i, i) for i in range(3)]
    rebuild_collection(client, "gestion_talento", chunks, ef=ef)
    col = open_collection(client, "gestion_talento", ef=ef)
    res = retrieve(col, "t1", 2)
    assert len(res) == 2 and res[0].source == "a.md"
    rebuild_collection(client, "gestion_talento", [], ef=ef)
    assert retrieve(open_collection(client, "gestion_talento", ef=ef), "x", 4) == []
