# Flock Talent Agent

Chat agent for Flock IT's "AI Day" that answers questions about the Talent Management process (Gestión de Talento) using RAG over `docs/*.md`. A one-day didactic demo: minimal, but it has to work.

## Stack (decided, don't re-litigate)

- **Python 3.9.6** (system, venv at `.venv`). No `X | Y` unions at runtime, no `match`, no `tomllib`. Use `from __future__ import annotations` or `Optional`.
- **Streamlit** for the chat UI (`app.py`).
- **ChromaDB** persisted at `./chroma_db`, using Chroma's default local embedding function. No embedding API.
- **LLM via OpenRouter**, a `:free` model, called through the `openai` SDK with `base_url=https://openrouter.ai/api/v1`.
- **NO LangChain / LangGraph.** The RAG loop is hand-written on purpose so it can be explained.

## Layout

- `docs/*.md`: the knowledge base, in Spanish.
- `rag/`: one small module per responsibility (config, chunking, store, retrieval, prompting, llm, pipeline, ui_helpers).
- `ingest.py`: a thin CLI that rebuilds the index.
- `app.py`: the thin Streamlit UI.
- `tests/`: pytest tests, run offline with fakes.
- `assets/`: Flock logos.
- `.streamlit/config.toml`: the theme.

## Commands

```bash
source .venv/bin/activate
pip install -r requirements.txt
.venv/bin/pytest            # must pass offline
python ingest.py            # rebuild index after any docs/ change
streamlit run app.py
```

## Rules

- **Strict TDD**: write the failing test first, then the code. Tests never hit the network: inject fakes for the Chroma collection, the embedding function and the LLM.
- **Ingestion is idempotent**: every run rebuilds the collection from scratch, with deterministic IDs.
- **Secrets**: `OPENROUTER_API_KEY` lives only in `.env`, which is gitignored. Never hardcode it or commit it. `.env.example` holds keys with no values.
- **Config by env**: `OPENROUTER_MODEL`, `TOP_K` (default 6).
- **UI**: all text in Spanish. Must follow the `flock-brand-design` skill: primary `#7F07C5`, accent `#FF5102` (accent only), dark `#44016B`.
- **Errors**: show friendly Spanish messages in the UI, never stack traces.

## Knowledge base (`docs/`)

- One `.md` per topic. The user pastes raw text, and Claude structures it:
  - `##`/`###` headings that repeat their context, so each chunk stands alone.
  - Tables for structured data.
  - No broken or noisy URLs.
- Never change the meaning of official content. Mark illustrative examples as such.
- After editing docs, re-run `python ingest.py`.

## Project skills (`.claude/skills/`)

- `flock-brand-design`: palette, gradients and logos. It overrides any default styling.
- `rag-implementation`: use it for concepts only. Its code uses LangChain, so don't copy it.
- `openrouter-models`: for picking or inspecting a `:free` model. Its scripts need `npm install` in `scripts/`.

## Workflow

- Planning lives in `openspec/` (SDD, file-based). Don't use engram for this project.
- Current change: `openspec/changes/rag-chat-mvp/`. Progress is in `tasks.md` and `apply-progress.md`.
- Never build after changes. Use conventional commits, with no AI attribution.
- For shell file operations, use `bat`/`rg`/`fd`/`sd`/`eza`, not `cat`/`grep`/`find`/`sed`/`ls`.

## Known risks

- Free OpenRouter providers may log prompts, and this is internal Flock data. The UI shows a warning about it.
- Free models can hit rate limits or disappear. Keep a fallback `OPENROUTER_MODEL`.
- The default embedding model is English-centric, so retrieval on Spanish paraphrases may be weaker. Swapping it is a one-line change in `rag/store.py`.
- Retrieval uses only the current question, so follow-ups like "¿y cuánto dura?" retrieve poorly.
