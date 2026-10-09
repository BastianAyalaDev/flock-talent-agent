"""Logica pura de la UI (sin streamlit): historial y estado del indice."""
from __future__ import annotations

from typing import Callable, Dict, List, Optional

from rag.pipeline import Answer


def is_blank(text: Optional[str]) -> bool:
    return text is None or not text.strip()


def append_message(
    history: List[Dict],
    role: str,
    content: str,
) -> bool:
    """Agrega un mensaje. Ignora contenido vacio; devuelve si agrego."""
    if is_blank(content):
        return False
    history.append({"role": role, "content": content})
    return True


def to_llm_history(history: List[Dict]) -> List[Dict]:
    return [{"role": m["role"], "content": m["content"]} for m in history]


def submit_question(
    history: List[Dict],
    text: Optional[str],
    answer_fn: Callable[[str, List[Dict]], Answer],
) -> bool:
    """Procesa una pregunta: ignora vacias; llama `answer_fn(pregunta, historial_previo)`
    y agrega el turno usuario + asistente al historial."""
    if is_blank(text):
        return False
    question = text.strip()
    prior = to_llm_history(history)
    result = answer_fn(question, prior)
    append_message(history, "user", question)
    append_message(history, "assistant", result.text)
    return True


def index_ready(collection) -> bool:
    """True si la coleccion existe y tiene al menos un chunk."""
    if collection is None:
        return False
    try:
        return collection.count() > 0
    except Exception:
        return False
