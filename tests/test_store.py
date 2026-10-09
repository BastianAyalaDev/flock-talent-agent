from __future__ import annotations

from rag.chunking import Chunk
from rag.store import open_collection, rebuild_collection
from tests.fakes import FakeEmbeddingFunction


def _chunks(source="a.md", n=3):
    return [
        Chunk(
            id="%s::%03d" % (source, i),
            text="Seccion %d\n\ncuerpo %d" % (i, i),
            source=source,
            section="Sec > Sub %d" % i,
            chunk_index=i,
        )
        for i in range(n)
    ]


def test_rebuild_devuelve_conteo(client):
    n = rebuild_collection(client, "gestion_talento", _chunks(n=3), ef=FakeEmbeddingFunction())
    assert n == 3


def test_guarda_metadata(client):
    ef = FakeEmbeddingFunction()
    rebuild_collection(client, "gestion_talento", _chunks(), ef=ef)
    col = open_collection(client, "gestion_talento", ef=ef)
    got = col.get(ids=["a.md::001"], include=["metadatas", "documents"])
    meta = got["metadatas"][0]
    assert meta["source"] == "a.md"
    assert meta["section"] == "Sec > Sub 1"
    assert meta["heading"] == "Sub 1"
    assert meta["chunk_index"] == 1
    assert got["documents"][0].startswith("Seccion 1")


def test_dos_veces_no_duplica(client):
    ef = FakeEmbeddingFunction()
    rebuild_collection(client, "gestion_talento", _chunks(), ef=ef)
    n = rebuild_collection(client, "gestion_talento", _chunks(), ef=ef)
    assert n == 3
    assert open_collection(client, "gestion_talento", ef=ef).count() == 3


def test_doc_eliminado_desaparece(client):
    ef = FakeEmbeddingFunction()
    rebuild_collection(client, "gestion_talento", _chunks(source="old.md"), ef=ef)
    rebuild_collection(client, "gestion_talento", _chunks(source="new.md", n=2), ef=ef)
    got = open_collection(client, "gestion_talento", ef=ef).get(include=["metadatas"])
    assert {m["source"] for m in got["metadatas"]} == {"new.md"}


def test_rebuild_sobre_coleccion_inexistente_no_falla(client):
    assert rebuild_collection(client, "nueva", _chunks(n=1), ef=FakeEmbeddingFunction()) == 1


def test_rebuild_sin_chunks_deja_coleccion_vacia(client):
    ef = FakeEmbeddingFunction()
    assert rebuild_collection(client, "gestion_talento", [], ef=ef) == 0
    assert open_collection(client, "gestion_talento", ef=ef).count() == 0


def test_open_collection_inexistente_devuelve_none(client):
    assert open_collection(client, "no_existe", ef=FakeEmbeddingFunction()) is None


def test_reingesta_con_handle_viejo_abre_la_nueva_coleccion(client):
    """Reproduce W2: tras re-ingestar, un handle cacheado queda obsoleto; abrir de nuevo sirve."""
    ef = FakeEmbeddingFunction()
    rebuild_collection(client, "gestion_talento", _chunks(source="v1.md", n=2), ef=ef)
    viejo = open_collection(client, "gestion_talento", ef=ef)
    assert viejo is not None

    rebuild_collection(client, "gestion_talento", _chunks(source="v2.md", n=3), ef=ef)
    nuevo = open_collection(client, "gestion_talento", ef=ef)

    assert nuevo is not None
    assert nuevo.count() == 3
    res = nuevo.query(query_texts=["cuerpo 1"], n_results=2)
    assert all(m["source"] == "v2.md" for m in res["metadatas"][0])
