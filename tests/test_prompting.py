from __future__ import annotations

from rag.prompting import NO_SE, build_messages
from rag.retrieval import RetrievedChunk

CHUNKS = [
    RetrievedChunk("Texto uno", "proceso.md", "Etapa 1 > Paso 1", 0.1),
    RetrievedChunk("Texto dos", "proceso.md", "Comité", 0.2),
]


def _history(turns):
    h = []
    for i in range(turns):
        h.append({"role": "user", "content": "pregunta %d" % i})
        h.append({"role": "assistant", "content": "respuesta %d" % i})
    return h


def test_system_prompt_solo_con_info_provista_y_no_se():
    system = build_messages("¿Qué es?", CHUNKS, [], 3)[0]
    assert system["role"] == "system"
    c = system["content"]
    assert "SOLO" in c and "INFORMACIÓN" in c
    assert "español" in c
    assert NO_SE in c
    assert NO_SE.startswith("No sé:")
    assert "documentación" not in NO_SE
    assert "people@flockit.com.ar" in NO_SE


def test_system_prompt_prohibe_conocimiento_general_aun_parcial():
    c = build_messages("¿Qué es?", CHUNKS, [], 3)[0]["content"]
    assert "documentación de Flock" in c
    assert "conocimiento general" in c
    assert "solo una parte" in c


def test_system_prompt_persona_es_asistente_de_flock_en_general():
    c = build_messages("¿Quién sos?", CHUNKS, [], 3)[0]["content"]
    assert c.startswith("Sos el asistente de Flock.")


def test_system_prompt_pide_comando_de_pibot_cuando_aplica():
    c = build_messages("¿Cómo pido feedback?", CHUNKS, [], 3)[0]["content"]
    assert "PIbot" in c
    assert "comando exacto" in c


def test_system_prompt_prohibe_citas_y_menciones_de_fuentes():
    c = build_messages("q", CHUNKS, [], 3)[0]["content"].lower()
    assert "[n]" not in c
    assert "nunca" in c
    assert "citas" in c and "[1]" in c  # prohibe marcadores de cita
    assert "archivos" in c  # prohibe nombrar archivos/fuentes
    assert "contexto" in c  # menciona que no se aluda al contexto
    assert "según el" in c


def test_system_prompt_pide_brevedad_y_oferta_final():
    c = build_messages("q", CHUNKS, [], 3)[0]["content"]
    assert "breve" in c.lower()
    assert "2 a 5 oraciones" in c
    assert "UNA" in c and "profundizar" in c
    assert "vos" in c or "voseo" in c.lower()


def test_mensaje_final_con_info_por_seccion_sin_numeros_ni_archivos():
    msgs = build_messages("¿Qué es el Comité?", CHUNKS, [], 3)
    last = msgs[-1]
    assert last["role"] == "user"
    body = last["content"]
    assert body.startswith("INFORMACIÓN:\n")
    assert "Etapa 1 > Paso 1" in body and "Texto uno" in body
    assert "Texto dos" in body
    assert "proceso.md" not in body
    assert "[1]" not in body and "[2]" not in body
    assert body.endswith("PREGUNTA: ¿Qué es el Comité?")
    assert body.index("Texto dos") < body.index("PREGUNTA:")


def test_recorta_historial_a_max_turns():
    msgs = build_messages("nueva", CHUNKS, _history(5), 3)
    # system + 6 historial + user final
    assert len(msgs) == 8
    assert msgs[1]["content"] == "pregunta 2"
    assert msgs[6]["content"] == "respuesta 4"
    assert [m["role"] for m in msgs[1:7]] == ["user", "assistant"] * 3


def test_historial_corto_se_conserva_y_sin_contexto_previo():
    hist = [{"role": "user", "content": "hola", "sources": ["x"]},
            {"role": "assistant", "content": "chau"}]
    msgs = build_messages("nueva", CHUNKS, hist, 3)
    assert msgs[1] == {"role": "user", "content": "hola"}
    assert msgs[2] == {"role": "assistant", "content": "chau"}
    assert all("INFORMACIÓN:" not in m["content"] for m in msgs[1:-1])


def test_max_turns_cero_no_incluye_historial():
    assert len(build_messages("q", CHUNKS, _history(2), 0)) == 2


def test_sin_chunks_indica_no_hay_contexto_y_mantiene_regla():
    msgs = build_messages("¿Capital de Francia?", [], [], 3)
    assert NO_SE in msgs[0]["content"]
    assert "no hay información" in msgs[-1]["content"].lower()
    assert msgs[-1]["content"].endswith("PREGUNTA: ¿Capital de Francia?")
