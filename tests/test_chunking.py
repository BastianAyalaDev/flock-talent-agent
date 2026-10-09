from rag.chunking import Chunk, chunk_markdown


def _by_section(chunks):
    return {c.section: c for c in chunks}


def test_divide_por_headings_h2():
    md = "# Doc\n\n## A\n\ntexto a\n\n## B\n\ntexto b\n"
    chunks = chunk_markdown(md, "x.md")

    assert [c.section for c in chunks] == ["A", "B"]
    assert chunks[0].text == "A\n\ntexto a"
    assert chunks[1].text == "B\n\ntexto b"
    assert all(isinstance(c, Chunk) and c.source == "x.md" for c in chunks)


def test_subseccion_h3_tiene_ruta_a_mayor_a1():
    md = "## A\n\nintro a\n\n### A1\n\ncuerpo a1\n\n### A2\n\ncuerpo a2\n\n## B\n\nb\n"
    chunks = chunk_markdown(md, "x.md")

    assert [c.section for c in chunks] == ["A", "A > A1", "A > A2", "B"]
    assert chunks[0].text == "A\n\nintro a"  # intro propia antes del primer ###
    assert chunks[1].text == "A > A1\n\ncuerpo a1"


def test_h2_sin_cuerpo_se_descarta():
    md = "## A\n\n### A1\n\ncuerpo\n"
    chunks = chunk_markdown(md, "x.md")
    assert [c.section for c in chunks] == ["A > A1"]


def test_fallback_por_tamano_respeta_max_y_repite_ruta():
    parrafos = ["p%d " % i + "x" * 80 for i in range(10)]
    md = "## Larga\n\n" + "\n\n".join(parrafos) + "\n"
    chunks = chunk_markdown(md, "x.md", max_chars=300)

    assert len(chunks) > 1
    for c in chunks:
        assert len(c.text) <= 300
        assert c.section == "Larga"
        assert c.text.startswith("Larga\n\n")
    # no se pierde ningun parrafo
    unidos = "\n".join(c.text for c in chunks)
    for p in parrafos:
        assert p in unidos


def test_parrafo_gigante_se_parte_sin_superar_max():
    md = "## G\n\n" + ("palabra " * 200) + "\n"
    chunks = chunk_markdown(md, "x.md", max_chars=200)
    assert len(chunks) > 1
    assert all(len(c.text) <= 200 for c in chunks)


def test_texto_previo_al_primer_h2_usa_h1_como_seccion():
    md = "# Titulo Doc\n\nintro suelta\n\n## A\n\na\n"
    chunks = chunk_markdown(md, "x.md")

    assert chunks[0].section == "Titulo Doc"
    assert chunks[0].text == "Titulo Doc\n\nintro suelta"
    assert chunks[1].section == "A"


def test_chunks_vacios_descartados():
    md = "# T\n\n## A\n\n   \n\n## B\n\nb\n"
    chunks = chunk_markdown(md, "x.md")
    assert [c.section for c in chunks] == ["B"]
    assert chunk_markdown("", "x.md") == []


def test_ids_deterministicos_secuenciales():
    md = "## A\n\na\n\n## B\n\nb\n\n## C\n\nc\n"
    chunks = chunk_markdown(md, "doc.md")

    assert [c.id for c in chunks] == ["doc.md::000", "doc.md::001", "doc.md::002"]
    assert [c.chunk_index for c in chunks] == [0, 1, 2]
    assert [c.id for c in chunk_markdown(md, "doc.md")] == [c.id for c in chunks]


def test_tabla_no_se_corta():
    tabla = "\n".join(["| a | b |", "|---|---|"] + ["| %d | %s |" % (i, "y" * 30) for i in range(8)])
    md = "## T\n\n" + "intro " + "z" * 100 + "\n\n" + tabla + "\n\nfin " + "w" * 100 + "\n"
    chunks = chunk_markdown(md, "x.md", max_chars=500)

    assert any(tabla in c.text for c in chunks)


def test_headings_dentro_de_code_fence_se_ignoran():
    md = "## A\n\n```\n## no es heading\n```\n"
    chunks = chunk_markdown(md, "x.md")
    assert [c.section for c in chunks] == ["A"]
    assert "## no es heading" in chunks[0].text
