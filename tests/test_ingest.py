from __future__ import annotations

import pytest

from ingest import IngestError, read_docs, run_ingest
from rag.store import open_collection
from tests.fakes import FakeEmbeddingFunction


def _write(tmp_path):
    (tmp_path / "a.md").write_text("## A\n\ntexto a\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("## B\n\ntexto b\n\n### B1\n\ntexto b1\n", encoding="utf-8")
    (tmp_path / "image.png").write_bytes(b"\x89PNG")


def test_read_docs_solo_markdown(tmp_path):
    _write(tmp_path)
    docs = read_docs(str(tmp_path))
    assert [name for name, _ in docs] == ["a.md", "b.md"]
    assert docs[0][1].startswith("## A")


def test_read_docs_sin_markdown_falla_en_espanol(tmp_path):
    (tmp_path / "image.png").write_bytes(b"x")
    with pytest.raises(IngestError) as exc:
        read_docs(str(tmp_path))
    assert "No encontré" in str(exc.value)


def test_read_docs_directorio_inexistente(tmp_path):
    with pytest.raises(IngestError):
        read_docs(str(tmp_path / "nope"))


def test_run_ingest_con_fake_indexa_sin_red(tmp_path, client):
    _write(tmp_path)
    ef = FakeEmbeddingFunction()
    n = run_ingest(str(tmp_path), client, ef=ef, collection_name="gestion_talento")
    assert n == 3
    got = open_collection(client, "gestion_talento", ef=ef).get(include=["metadatas", "documents"])
    assert set(got["ids"]) == {"a.md::000", "b.md::000", "b.md::001"}
    assert {m["source"] for m in got["metadatas"]} == {"a.md", "b.md"}
    assert all(d for d in got["documents"])


def test_run_ingest_idempotente(tmp_path, client):
    _write(tmp_path)
    ef = FakeEmbeddingFunction()
    assert run_ingest(str(tmp_path), client, ef=ef) == run_ingest(str(tmp_path), client, ef=ef)
    assert open_collection(client, "gestion_talento", ef=ef).count() == 3


def test_rutas_por_defecto_son_absolutas_y_apuntan_al_repo():
    import os

    import ingest

    assert os.path.isabs(ingest.DOCS_DIR) and os.path.isdir(ingest.DOCS_DIR)
    assert os.path.isabs(ingest.CHROMA_PATH)
    assert os.path.dirname(ingest.CHROMA_PATH) == os.path.dirname(os.path.abspath(ingest.__file__))
