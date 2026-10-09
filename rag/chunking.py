"""Chunking de markdown por headings (##/###) con fallback por tamano. Puro, sin I/O."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

_HEADING = re.compile(r"^(#{1,3})\s+(.*\S)\s*$")
_MIN_BUDGET = 50  # evita presupuesto <= 0 si la ruta es mas larga que max_chars
_FENCE = re.compile(r"^\s*(```|~~~)")


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source: str
    section: str
    chunk_index: int


def chunk_markdown(text: str, source: str, max_chars: int = 1500) -> List[Chunk]:
    """Divide `text` en chunks por headings. Texto de cada chunk: "{ruta}\\n\\n{cuerpo}"."""
    chunks: List[Chunk] = []
    for section, body in _sections(text):
        for part in _split_body(body, max(max_chars - len(section) - 2, _MIN_BUDGET)):
            index = len(chunks)
            chunks.append(
                Chunk(
                    id="%s::%03d" % (source, index),
                    text="%s\n\n%s" % (section, part),
                    source=source,
                    section=section,
                    chunk_index=index,
                )
            )
    return chunks


def _sections(text: str) -> List[Tuple[str, str]]:
    """Devuelve [(ruta, cuerpo)] en orden, sin cuerpos vacios."""
    h1: Optional[str] = None
    h2: Optional[str] = None
    path = ""
    lines: List[str] = []
    out: List[Tuple[str, str]] = []
    in_fence = False

    def flush() -> None:
        body = "\n".join(lines).strip()
        if body and path:
            out.append((path, body))
        del lines[:]

    for line in text.splitlines():
        if _FENCE.match(line):
            in_fence = not in_fence
        m = None if in_fence else _HEADING.match(line)
        if not m:
            lines.append(line)
            continue
        level, title = len(m.group(1)), m.group(2)
        if level == 1:
            flush()
            h1, h2, path = title, None, title
        elif level == 2:
            flush()
            h2, path = title, title
        else:
            flush()
            path = "%s > %s" % (h2, title) if h2 else title
    flush()
    return out


def _split_body(body: str, budget: int) -> List[str]:
    """Parte el cuerpo en trozos <= budget acumulando parrafos (bloques separados por linea en blanco)."""
    if len(body) <= budget:
        return [body]
    parts: List[str] = []
    current = ""
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if not block:
            continue
        for piece in _hard_split(block, budget):
            candidate = piece if not current else current + "\n\n" + piece
            if len(candidate) <= budget:
                current = candidate
            else:
                parts.append(current)
                current = piece
    if current:
        parts.append(current)
    return parts


def _hard_split(block: str, budget: int) -> List[str]:
    """Un bloque que no entra solo se parte por lineas y, si hace falta, por palabras/caracteres."""
    if len(block) <= budget:
        return [block]
    pieces: List[str] = []
    current = ""
    for line in block.split("\n"):
        for unit in _split_long(line, budget):
            candidate = unit if not current else current + "\n" + unit
            if len(candidate) <= budget:
                current = candidate
            else:
                pieces.append(current)
                current = unit
    if current:
        pieces.append(current)
    return pieces


def _split_long(line: str, budget: int) -> List[str]:
    if len(line) <= budget:
        return [line]
    out: List[str] = []
    current = ""
    for word in line.split(" "):
        while len(word) > budget:
            if current:
                out.append(current)
                current = ""
            out.append(word[:budget])
            word = word[budget:]
        candidate = word if not current else current + " " + word
        if len(candidate) <= budget:
            current = candidate
        else:
            out.append(current)
            current = word
    if current:
        out.append(current)
    return out
