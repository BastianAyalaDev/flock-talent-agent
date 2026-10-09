"""Orquesta el loop RAG: retrieve -> build_messages -> llm."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

from rag.llm import LLM, LLMError
from rag.prompting import build_messages
from rag.retrieval import RetrievedChunk, retrieve


@dataclass(frozen=True)
class Answer:
    text: str
    sources: List[RetrievedChunk] = field(default_factory=list)


_CITATION = re.compile(r"[ \t]*\[\d+(?:\s*,\s*\d+)*\]")


def strip_citations(text: str) -> str:
    """Red de seguridad: quita marcadores tipo [1] o [2, 3] que el modelo pudiera emitir."""
    return _CITATION.sub("", text).strip()


def _unique_sources(chunks: List[RetrievedChunk]) -> List[RetrievedChunk]:
    seen = set()
    unique = []
    for c in chunks:
        key = (c.source, c.section)
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


def answer(
    question: str,
    history: List[Dict],
    collection,
    llm: LLM,
    k: int,
    max_turns: int,
) -> Answer:
    """Responde (las fuentes se conservan internamente, la UI no las muestra). Ante LLMError devuelve el mensaje amigable y sin fuentes."""
    chunks = retrieve(collection, question, k)
    messages = build_messages(question, chunks, history, max_turns)
    try:
        text = llm(messages)
    except LLMError as exc:
        return Answer(text=str(exc), sources=[])
    return Answer(text=strip_citations(text), sources=_unique_sources(chunks))
