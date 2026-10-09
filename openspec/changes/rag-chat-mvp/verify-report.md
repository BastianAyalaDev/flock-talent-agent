# Verification Report

**Change**: rag-chat-mvp
**Version**: N/A (delta specs: knowledge-ingestion, rag-query, chat-ui)
**Mode**: Strict TDD
**Date**: 2026-10-09

---

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 41 |
| Tasks complete | 37 |
| Tasks incomplete | 4 (all manual-pending, they need the user's real API key) |

Incomplete tasks, all classified as **manual-pending**, not implementation failures:
- 7.4 Create a real `.env` with the API key. The accent-contrast part is done.
- 8.4 Ask 3 to 5 real questions with the LLM.
- 8.5 Ask an out-of-scope question and check for the exact "No sé..." reply.
- 8.6 Check the invalid-key case. Empty input and missing index are covered by unit tests.
- 8.3 is marked [x], but the visual browser review (theme and logos) is still pending.

---

## Build & Tests Execution

**Build**: N/A. There is no build step, and the user's rules say never to build. `py_compile` on `app.py`, `ingest.py` and `rag/*.py` passes.

**Tests**: 70 passed, 0 failed, 0 skipped (`.venv/bin/pytest`, offline, 0.57s)
```
......................................................................   [100%]
70 passed in 0.57s
```
Per file: branding 2, chunking 10, chunking_proceso 4, config 6, ingest 5, llm 11, pipeline 5, prompting 6, retrieval 4, store 6, ui_helpers 11.

**Coverage**: Not available, because `pytest-cov` and `coverage` are not installed.

---

## TDD Compliance

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | Partial | The evidence exists as a per-batch narrative (RED cause, GREEN count, REFACTOR) in apply-progress.md, but not in the required "TDD Cycle Evidence" table |
| All tasks have tests | Yes | Every testable module task (2.x to 7.2) has a test file. 6.3 `app.py` is manual by design |
| RED confirmed (tests exist) | Yes | 11 of 11 test files reported by apply exist |
| GREEN confirmed (tests pass) | Yes | 70 of 70 pass on execution now |
| Triangulation adequate | Yes | Multiple distinct-value cases per behavior (chunking 10 cases, llm 5 error kinds plus 3 empty variants, etc.) |
| Safety Net for modified files | Yes | `rag/config.py` was modified in batch 7, and the full suite ran (70 passed) |

**TDD Compliance**: 5/6 checks fully passed (1 format deviation)

## Test Layer Distribution

| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 57 | 9 | pytest + fakes |
| Integration (Chroma EphemeralClient + fake EF) | 13 | 3 (store 6, ingest 3, retrieval 1 + reads) | pytest + chromadb in-memory |
| E2E / UI | 0 | 0 | not installed (AppTest was used ad hoc during apply, not committed) |
| **Total** | **70** | **11** | |

## Changed File Coverage
Coverage analysis was skipped because no coverage tool is installed.

## Assertion Quality
No tautologies, ghost loops or assertions without production calls were found. The empty-result checks (`retrieve` returns `[]`, `format_sources([])` returns `""`) all have non-empty companion tests. `test_defaults` asserts only that `s.model` is truthy, but it does so alongside value assertions, which is acceptable.
One gap: `tests/test_pipeline.py::test_prompt_enviado_contiene_regla_no_se_y_la_pregunta` never asserts the returned `Answer.text` (see W5).

**Assertion quality**: 0 CRITICAL, 1 WARNING

## Quality Metrics
**Linter**: Not available
**Type Checker**: Not available
**Python 3.9 compat**: OK. `rg` found no `match`, `tomllib`, or runtime `X | Y`. Every module uses `from __future__ import annotations` plus `typing.List/Optional`. The branding test uses a regex instead of tomllib.

---

## Spec Compliance Matrix

### knowledge-ingestion
| Requirement | Scenario | Test | Result |
|---|---|---|---|
| Lectura de documentos | Solo markdown | `test_ingest.py > test_read_docs_solo_markdown` | COMPLIANT |
| Lectura de documentos | Directorio sin markdown | `test_ingest.py > test_read_docs_sin_markdown_falla_en_espanol` (+ `_directorio_inexistente`) | COMPLIANT |
| Chunking por headings | División por headings | `test_chunking.py > test_divide_por_headings_h2` | COMPLIANT |
| Chunking por headings | Subsección anidada | `test_chunking.py > test_subseccion_h3_tiene_ruta_a_mayor_a1` | COMPLIANT |
| Chunking por headings | Fallback por tamaño | `test_chunking.py > test_fallback_por_tamano_respeta_max_y_repite_ruta`, `test_parrafo_gigante_se_parte_sin_superar_max` | COMPLIANT |
| Chunking por headings | Texto previo al primer heading | `test_chunking.py > test_texto_previo_al_primer_h2_usa_h1_como_seccion` | COMPLIANT |
| Metadata de chunks | Metadata presente | `test_store.py > test_guarda_metadata` + `test_chunking_proceso.py > test_proceso_tiene_seccion_comite` | COMPLIANT |
| Indexado idempotente | Re-ejecución sin duplicados | `test_store.py > test_dos_veces_no_duplica`, `test_ingest.py > test_run_ingest_idempotente` (+ real run: 38/38) | COMPLIANT |
| Indexado idempotente | Doc eliminado | `test_store.py > test_doc_eliminado_desaparece` | COMPLIANT |
| Testabilidad sin red | Ingesta con fake | `test_ingest.py > test_run_ingest_con_fake_indexa_sin_red` | COMPLIANT |

### rag-query
| Requirement | Scenario | Test | Result |
|---|---|---|---|
| Retrieval top-k | Devuelve k resultados | `test_retrieval.py > test_devuelve_k_resultados_en_orden` | COMPLIANT |
| Retrieval top-k | Colección vacía | `test_retrieval.py > test_coleccion_vacia_devuelve_lista_vacia`, `test_con_chroma_real_en_memoria` | COMPLIANT |
| Armado de prompt | Prompt completo | `test_prompting.py > test_system_prompt_tiene_las_reglas`, `test_mensaje_final_con_contexto_numerado_y_pregunta` | COMPLIANT |
| Armado de prompt | Sin contexto | `test_prompting.py > test_sin_chunks_indica_no_hay_contexto_y_mantiene_regla` | COMPLIANT |
| Cliente LLM OpenRouter | Configuración por env | `test_config.py > test_lee_key_model_y_top_k_del_entorno` + `test_llm.py > test_sin_client_construye_openai_apuntando_a_openrouter`, `test_usa_el_modelo_dado_y_devuelve_el_texto` | COMPLIANT |
| Cliente LLM OpenRouter | Falta la clave | `test_config.py > test_falta_api_key_lanza_config_error_en_espanol`, `test_api_key_en_blanco_lanza_config_error` | COMPLIANT |
| Respuesta con fuentes | Respuesta con fake | `test_pipeline.py > test_devuelve_texto_y_fuentes`, `test_fuentes_sin_duplicados` | COMPLIANT |
| Respuesta con fuentes | Pregunta fuera de contexto | `test_pipeline.py > test_prompt_enviado_contiene_regla_no_se_y_la_pregunta` (does not assert the returned text) | PARTIAL (+ manual 8.5 pending) |
| Manejo de errores del LLM | LLM falla | `test_pipeline.py > test_llmerror_devuelve_mensaje_amigable_sin_fuentes` + `test_llm.py > test_errores_de_openai_se_traducen_a_llmerror[*]` | COMPLIANT |
| Sin red en tests | Suite offline | Whole suite: 70 passed, fake EF, fake LLM clients | COMPLIANT |

### chat-ui
| Requirement | Scenario | Test | Result |
|---|---|---|---|
| Chat con historial | Mensaje nuevo | `test_ui_helpers.py > test_submit_question_agrega_turno_con_fuentes_y_pasa_historial_previo` | COMPLIANT |
| Chat con historial | Persistencia entre reruns | `test_ui_helpers.py > test_append_message_guarda_fuentes_con_el_mensaje_y_en_orden` (ordering only, no rerun) | PARTIAL (rerun via `st.session_state` not tested) |
| Chat con historial | Entrada vacía | `test_ui_helpers.py > test_submit_question_vacia_no_llama_al_pipeline`, `test_append_message_ignora_vacios`, `test_is_blank` | COMPLIANT |
| Fuentes visibles | Fuentes bajo la respuesta | `test_ui_helpers.py > test_format_sources_una_linea_por_fuente`, `test_format_source_incluye_archivo_y_seccion` | PARTIAL (no test of the expander rendering) |
| Fuentes visibles | Respuesta sin fuentes | `test_ui_helpers.py > test_submit_question_respuesta_sin_fuentes`, `test_format_sources_lista_vacia_es_cadena_vacia` | COMPLIANT |
| Estado de carga y errores | Índice inexistente | `test_ui_helpers.py > test_index_ready` (the decision only; the `st.warning` text is not tested) | PARTIAL |
| Branding Flock | Tema configurado | `test_branding.py > test_tema_flock_configurado` | COMPLIANT |
| Branding Flock | Assets de marca | `test_branding.py > test_assets_de_marca_existen` | COMPLIANT |
| Idioma y privacidad | Textos en español | Manual. A static read of `app.py` shows all strings in Spanish and the privacy caption in the sidebar | MANUAL (visual pending) |
| Testabilidad | Formateo de fuentes | `test_ui_helpers.py > test_format_source_incluye_archivo_y_seccion` | COMPLIANT |

**Compliance summary**: 25/30 scenarios fully COMPLIANT, 4 PARTIAL, 1 MANUAL, 0 FAILING, 0 UNTESTED.

---

## Correctness (Static, Structural Evidence)

| Requirement | Status | Notes |
|---|---|---|
| Lectura de documentos | Implemented | `ingest.read_docs` filters `.md` and raises `IngestError` in Spanish |
| Chunking por headings | Implemented | `rag/chunking.py`: path `A > A1`, budget = max - len(path) - 2, code fences ignored |
| Metadata de chunks | Implemented | `source/section/heading/chunk_index` in `store.rebuild_collection` |
| Indexado idempotente | Implemented | delete + create, IDs `"{source}::{i:03d}"`. Real run gave 38 chunks twice |
| Testabilidad sin red | Implemented | client and EF are injectable |
| Retrieval top-k | Implemented | Default 4 from env `TOP_K`. Quality concern, see W1 |
| Armado de prompt | Implemented | System prompt matches the design. `[n] (archivo — sección)` numbering |
| Cliente LLM OpenRouter | Implemented | `openai.OpenAI(base_url="https://openrouter.ai/api/v1")`, model from env with default `google/gemma-4-31b-it:free`. No hardcoded key (`rg "sk-or-"`: 0 hits) |
| Respuesta con fuentes | Implemented | Deduplicated by (source, section) |
| Manejo de errores del LLM | Implemented | `LLMError` with friendly messages. `app.py` also catches unexpected exceptions |
| Chat con historial / Fuentes / Carga / Branding / Idioma | Implemented | `app.py` has a spinner, a "Fuentes" expander only when there are sources, `st.error` on ConfigError, `st.warning` when the index is missing, and a privacy caption |
| Security | OK | `.env` is gitignored and absent. `.env.example` has empty values. No `sk-or-` anywhere |
| No LangChain | OK | Not in requirements, not imported, not installed in `.venv` |

---

## Coherence (Design)

| Decision | Followed? | Notes |
|---|---|---|
| Default Chroma embeddings, single swap point | Yes | `store.embedding_function()` |
| Chunking by headings + paragraph fallback, MAX 1500 | Yes | Plus a hard split by lines and words for oversized blocks (an improvement) |
| Heading path in chunk text + metadata | Yes | |
| Rebuild collection, deterministic IDs | Yes | |
| Top-k = 4, no distance threshold | Yes | Retrieval quality is weak on some questions, see W1 |
| History: last 3 turns, no prior context; retrieval on current question only | Yes | |
| Deterministic sources | Yes | |
| Errors translated (`LLMError`, `ConfigError`) | Yes | |
| File Changes table | Yes | Plus `tests/fakes.py`, `tests/conftest.py`, `pytest.ini`, `README.md` (all reasonable) |
| Interfaces | Yes, with minor deviation | `load_settings(env_file=".env")` gained a parameter, documented in apply-progress |
| Brand (flock-brand-design) | Yes | Primary `#7F07C5` in the theme. `#FF5102` appears only as the gradient end, with white 1.5rem bold text. The color logo is used through `st.logo` (sidebar/header on white), never over the gradient |

---

## Retrieval assessment: should the default TOP_K be raised?

I re-ran the check against a copy of the real index (38 chunks), using the real ONNX embedding and k=8:

| Question | Relevant hits in top-4 | Relevant hits in top-6 |
|---|---|---|
| ¿Cuáles son los pasos del F360? | Paso 5, 1, 2 (3 of 5 steps; rank 2 is Timeline) | +Paso 4 (4 of 5). **Paso 3 is not in the top 8**. The `## Etapa 1` intro chunk is not in the top 8 either |
| ¿Cuál es el rol del Comité? | **0 Comité chunks**. All 4 are "Espacio Champion" sections (the embedding latches onto "rol") | +"Comité > Criterios para presentar un caso" (rank 6). **The `## Etapa 3: Comité` intro (the actual answer) is not in the top 8** |
| ¿Qué es el Talent Review? | Etapa 2 at rank 1 | Same |
| ¿Qué es el Espacio Champion? | Correct sections | Same |
| ¿Qué buenas prácticas hay para Champions? | BP 4, 3, 5, 2 | +BP 1 (rank 6) |

Correction to the premise: the doc has **5** F360 steps (not 4), and top-4 retrieves 3 of them. The apply-progress claim that "las 5 preguntas traen la sección relevante" with k=4 does **not** hold for the Comité question.

**Verdict on TOP_K=6: advisable.**
- The cost is small. Chunks are at most 1500 chars, so 6 chunks come to about 9k chars (about 2.5k to 3k tokens), which is trivial for the 262k context of `gemma-4-31b-it`.
- It recovers the 4th F360 step, the first Comité section, and the 5th good practice.
- The risk is somewhat more off-topic context (Champion sections), but the system prompt's "only CONTEXT" plus `[n]` citations handle that.

**It is not sufficient on its own.** The intro chunks for Etapa 1 and Etapa 3 and Paso 3 miss even at k=8. That is the known weakness of the English-centric embedding on Spanish text. Real fixes, in order of cost:
1. Raise the default to k=6. Strict TDD order: RED in `test_config.py::test_defaults`, then `rag/config.py`, then `.env.example`, then CLAUDE.md and the design.
2. Swap `store.embedding_function()` to a multilingual model and re-run ingest. It is a one-line change, but sentence-transformers pulls in torch (about 1 GB).
3. A cheap lexical boost: re-rank by keyword overlap with the section path.

---

## Issues Found

**CRITICAL** (must fix before archive): None.

**WARNING** (should fix):
- **W1. Retrieval quality at the default TOP_K=4.** "¿Cuál es el rol del Comité?" retrieves no Comité chunk, and the F360 steps question gets 3 of 5 steps. This is a likely visible failure in the live demo (8.4 lists "rol del Comité" as a demo question). Raising TOP_K to 6 is advisable but only partial (see the assessment above). The apply-progress retrieval sanity claim is inaccurate for this question.
- **W2. Stale cached collection after re-ingest.** In `app.py`, `get_collection` is wrapped in `@st.cache_resource`. `rebuild_collection` deletes and recreates the collection, which gives it a new id. I reproduced this across processes: after `python ingest.py` runs while Streamlit is up, `index_ready(cached)` returns False (NotFoundError) and the query raises `NotFoundError: Collection [...] does not exist`. The app then gets stuck on "Todavía no hay un índice..." until the server restarts or the cache is cleared. This matters because CLAUDE.md says to re-run ingest after editing docs. Possible fixes: cache only the client and call `get_collection` on every run, or call `get_collection.clear()` when `index_ready` is False.
- **W3. TDD evidence format.** apply-progress.md has no "TDD Cycle Evidence" table. The RED/GREEN/REFACTOR evidence is narrative per batch. The substance is verifiable (all test files exist and pass), so this is not CRITICAL, but it does not follow the protocol format.
- **W4. Chat-UI scenarios only partially automated.** Persistence across reruns, the sources expander rendering, and the index-missing warning text are covered only at the helper level. The `streamlit.testing.v1.AppTest` checks done during apply were not committed to `tests/`.
- **W5. Weak assertion in the out-of-context scenario.** `tests/test_pipeline.py::test_prompt_enviado_contiene_regla_no_se_y_la_pregunta` never asserts `res.text == NO_SE`, so the "se muestra la respuesta del LLM" part of the scenario is unverified.

**SUGGESTION** (nice to have):
- S1. Commit AppTest-based tests for `app.py`: the no-key error, the empty-index warning, and the sources expander shown only when sources exist. This closes W4 offline.
- S2. Resolve `ISOTIPO`/`LOGO` in `app.py` and `DOCS_DIR`/`CHROMA_PATH` in `ingest.py` relative to `__file__`, so both work when launched from outside the repo root.
- S3. `tests/test_chunking_proceso.py::test_proceso_no_pierde_contenido` hardcodes a doc phrase, so it breaks on legitimate doc edits. Consider deriving checks from the headings instead.
- S4. Add `pytest-cov` (dev) to enable changed-file coverage in future verifies.
- S5. Update stale config and docs: `openspec/config.yaml` still has `testing.runner.installed: false` and all layers unavailable, and design.md says "~45 chunks" (the real count is 38). Update TOP_K references if W1 is applied.
- S6. Log or show the distance per source in the "Fuentes" expander, with a debug toggle. It is didactic for the demo and helps diagnose W1 live.

**MANUAL-PENDING** (need the user's API key or a browser, not counted as failures): 7.4 (`.env`), 8.4 (real answers), 8.5 (exact "No sé" reply), 8.6 invalid-key path, and the 8.3 visual check of the theme and logos.

---

## Verdict
**PASS WITH WARNINGS**

The implementation matches the specs and the design. 70 of 70 tests pass offline, with no hardcoded keys, no LangChain, and Python 3.9-safe code. Fix W1 (retrieval or TOP_K) and W2 (stale cache) before the live demo, then complete the manual-pending items with the real API key.
