from pathlib import Path

from rag.chunking import chunk_markdown

DOC = Path(__file__).resolve().parent.parent / "docs" / "proceso.md"


def _chunks():
    return chunk_markdown(DOC.read_text(encoding="utf-8"), DOC.name)


def test_proceso_chunks_validos():
    chunks = _chunks()

    assert len(chunks) > 10
    assert all(c.text.strip() for c in chunks)
    assert all(len(c.text) <= 1500 for c in chunks)
    assert all(c.source == "proceso.md" for c in chunks)


def test_proceso_ids_unicos():
    ids = [c.id for c in _chunks()]
    assert len(ids) == len(set(ids))


def test_proceso_tiene_seccion_comite():
    assert any("Comité" in c.section for c in _chunks())


def test_proceso_no_pierde_contenido():
    texto = DOC.read_text(encoding="utf-8")
    unidos = "\n".join(c.text for c in _chunks())
    # una frase del cuerpo de la intro y del final deben estar presentes
    assert "Acompañamos el desarrollo profesional de cada flocker" in unidos
    ultima = [l for l in texto.splitlines() if l.strip()][-1]
    assert ultima.strip() in unidos
