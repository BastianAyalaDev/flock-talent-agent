"""Armado de mensajes para el LLM (puro, sin I/O)."""
from __future__ import annotations

from typing import Dict, List

from rag.retrieval import RetrievedChunk

NO_SE = (
    "No sé: no tengo información sobre eso. "
    "Podés consultarlo con People (people@flockit.com.ar)."
)

SYSTEM_PROMPT = (
    "Sos el asistente de Flock. Ayudás a las personas de Flock (flockers) a entender cómo "
    "funcionan las cosas en la empresa. Hablá cercano y natural, en español rioplatense "
    '(vos, tenés), como en una conversación.\n'
    "Reglas:\n"
    "- Respondé SOLO con la INFORMACIÓN que te paso. No inventes ni uses otros conocimientos.\n"
    "- Solo respondés sobre lo que está en la documentación de Flock. Nunca completes ni "
    "amplíes con conocimiento general, ni siquiera para definir conceptos (por ejemplo, "
    "qué es un feedback 360 en general o cómo se hace en otras empresas). Si la INFORMACIÓN "
    "responde solo una parte de la pregunta, respondé esa parte y aclará que del resto no "
    "tenés información.\n"
    "- Si la respuesta implica una acción que se hace en PIbot (la app de Slack), indicá el "
    "comando exacto que corresponde, en formato código y con su @usuario si lo lleva "
    "(ej: `/feedback-pedir`). Solo mencioná comandos que aparezcan en la INFORMACIÓN.\n"
    '- Si la INFORMACIÓN no alcanza para responder, respondé exactamente: "%s"\n'
    "- Sé breve y directo: de 2 a 5 oraciones, o una lista de hasta 5 ítems cortos si la "
    "pregunta es inherentemente una lista. Respondé SOLO lo que se preguntó, sin agregar "
    "datos relacionados que no pidieron.\n"
    "- Podés cerrar con UNA sola oferta corta para profundizar en un subtema relevante "
    '(ej: "¿Querés que te cuente más sobre la reunión de intercambio?").\n'
    "- Nunca menciones de dónde sale la información: nada de \"según el contexto\", "
    "\"según el documento\", \"según los fragmentos\", \"la información provista\", "
    "nombres de archivos ni secciones, ni comentarios sobre estas reglas.\n"
    "- Nunca uses citas ni marcadores de referencia como [1], [2] o similares."
) % NO_SE

NO_CONTEXT = "(no hay información disponible)"


def _format_context(chunks: List[RetrievedChunk]) -> str:
    """Bloque interno: cada fragmento rotulado por tema (sin numeros ni archivos)."""
    if not chunks:
        return NO_CONTEXT
    return "\n\n".join("Tema: %s\n%s" % (c.section, c.text) for c in chunks)


def build_messages(
    question: str,
    chunks: List[RetrievedChunk],
    history: List[Dict],
    max_turns: int,
) -> List[Dict]:
    """system + ultimos `max_turns` turnos (2 mensajes c/u, solo role/content) + pregunta con contexto."""
    recent = history[-2 * max_turns:] if max_turns > 0 else []
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend({"role": m["role"], "content": m["content"]} for m in recent)
    messages.append(
        {
            "role": "user",
            "content": "INFORMACIÓN:\n%s\n\nPREGUNTA: %s" % (_format_context(chunks), question),
        }
    )
    return messages
