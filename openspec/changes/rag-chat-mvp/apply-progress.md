# Apply progress: rag-chat-mvp

## Batch 1 - Fase 1 (tareas 1.1-1.6) COMPLETA

Entorno: Python 3.9.6 (sistema), venv en `.venv`.

Versiones fijadas (pip freeze tras instalar): chromadb==1.5.9, openai==2.48.0, python-dotenv==1.2.1, streamlit==1.50.0, pytest==8.4.2.

Creado: requirements.txt, .gitignore (incluye node_modules/), .env.example, pytest.ini (testpaths=tests, pythonpath=.), rag/__init__.py, tests/conftest.py, assets/flock-logo-color.png, assets/flock-isotipo.png, README.md (es).

Verificacion: `.venv/bin/pytest` -> "collected 0 items", exit code 5 (esperado, sin tests aun).

Desvios: ninguno. Nota: Python 3.9 es antiguo; cuidado con sintaxis `X | Y` en type hints (usar `from __future__ import annotations` o Optional) y con `tomllib` (3.11+, usado en tarea 7.2: no disponible en 3.9).

## Batch 2 - Fase 2 (tareas 2.1-2.6) COMPLETA

Creado: rag/config.py, rag/chunking.py, tests/test_config.py, tests/test_chunking.py, tests/test_chunking_proceso.py.

TDD:
- 2.1 RED: ModuleNotFoundError rag.config (error de coleccion). 2.2 GREEN: 6 passed.
- 2.3 RED: ModuleNotFoundError rag.chunking. 2.4 GREEN: 20 passed (config 6 + chunking 10 + proceso 4).
- 2.5: tests con fixture real escritos junto a 2.3 (RED por modulo ausente); pasaron en GREEN sin ajustar chunking.
- 2.6 REFACTOR: guard _MIN_BUDGET=50 contra presupuesto <=0; suite verde.

Decisiones/desvios:
- `load_settings(env_file=".env")`: parametro extra para que los tests no lean .env real; load_dotenv(override=False) (el entorno gana).
- DEFAULT_MODEL provisorio `meta-llama/llama-3.3-70b-instruct:free` en config.py; se cierra en tarea 7.3.
- ConfigError tambien para TOP_K invalido (no entero o < 1).
- Headings dentro de code fences se ignoran. Tablas: solo se parten por lineas si un bloque solo excede el maximo (caso extremo).
- Presupuesto de cuerpo = max_chars - len(ruta) - 2, asi el texto completo del chunk nunca excede max_chars.
- Resultado en docs/proceso.md: ver conteo en reporte (chunks, max longitud).

## Batch 3 - Fase 3 (tareas 3.1-3.5) COMPLETA

Creado: rag/store.py, ingest.py, tests/fakes.py (FakeEmbeddingFunction determinista, hereda de chromadb EmbeddingFunction con name/get_config/build_from_config), fixture `client` en tests/conftest.py (EphemeralClient con allow_reset + reset antes/despues, porque EphemeralClient comparte estado en el proceso), tests/test_store.py (6), tests/test_ingest.py (5).

TDD:
- 3.1 RED: ModuleNotFoundError rag.store. 3.2 GREEN: primer intento fallo 5/6 por un bug del test (nombre de coleccion "gt" invalido en chroma: minimo 3 chars); se corrigio el test a "gestion_talento" -> 6 passed.
- 3.3 RED: ModuleNotFoundError ingest. 3.4 GREEN: suite 31 passed.
- 3.5 REFACTOR: sin cambios necesarios.

Decisiones: `IngestError` (en ingest.py) para directorio ausente/sin .md, mensajes en espanol; `read_docs` devuelve [(nombre, texto)] ordenado; `run_ingest(docs_dir, client, ef=None, collection_name="gestion_talento")`; `main()` devuelve exit code 1 con mensaje en stderr ante IngestError. `heading` = ultimo segmento de la ruta `A > B`. `rebuild_collection` captura NotFoundError/ValueError al borrar y soporta lista vacia. `open_collection` usa get_collection con el mismo EF. No se ejecuto `python ingest.py` real (tarea 8.2).

## Batch 4 - Fase 4 (tareas 4.1-4.5) COMPLETA

Creado: rag/retrieval.py, rag/prompting.py, tests/test_retrieval.py (4, incluye 1 de integracion con Chroma en memoria), tests/test_prompting.py (6).

TDD:
- 4.1 RED: ModuleNotFoundError rag.retrieval. 4.2 GREEN: 3 passed (luego +1 integracion, verde).
- 4.3 RED: ModuleNotFoundError rag.prompting. 4.4 GREEN: suite 40 passed; con integracion 41.
- 4.5 REFACTOR: sin cambios necesarios; suite verde.

Decisiones: `retrieve` llama `collection.query(query_texts=[q], n_results=k)`. `prompting.NO_SE` exporta la frase exacta; `build_messages` filtra el historial a role/content (descarta `sources`), recorta a los ultimos 2*max_turns mensajes (max_turns<=0 -> sin historial); sin chunks el mensaje dice "(no hay contexto disponible)".

## Batch 5 - Fase 5 (tareas 5.1-5.5) COMPLETA

Creado: rag/llm.py, rag/pipeline.py, tests/test_llm.py (11), tests/test_pipeline.py (5).

TDD:
- 5.1 RED: ImportError (rag.llm no existe). 5.2 GREEN: 11 passed.
- 5.3 RED: ModuleNotFoundError rag.pipeline. 5.4 GREEN: suite 57 passed.
- 5.5 REFACTOR: sin cambios; suite verde.

Decisiones: `make_llm(api_key, model, client=None)` usa `OpenAI(base_url=https://openrouter.ai/api/v1)`; excepts en orden RateLimitError, AuthenticationError, (APIConnectionError, APIStatusError) (APITimeoutError es subclase de APIConnectionError). Respuesta vacia/None/sin choices -> LLMError generico. `answer` captura LLMError y devuelve `Answer(str(exc), [])`; fuentes deduplicadas por (source, section) conservando orden.

## Batch 6 - Fase 6 (tareas 6.1-6.4) COMPLETA

Creado: rag/ui_helpers.py, tests/test_ui_helpers.py (11), app.py (sin tests, verificacion manual en fase 8).

TDD:
- 6.1 RED: ModuleNotFoundError rag.ui_helpers. 6.2 GREEN: suite 68 passed.
- 6.3 app.py: solo `py_compile` (no se lanzo streamlit).
- 6.4 REFACTOR: app.py sin logica propia salvo render; import de Answer al tope, render_message reutilizado.

Helpers: format_source, format_sources (lista Markdown, "" si vacia), is_blank, append_message (guarda `sources` con el mensaje), to_llm_history, submit_question(history, text, answer_fn) (ignora vacios, pasa historial previo), index_ready(collection).
app.py: set_page_config+st.logo con isotipo, header gradiente #44016B->#FF5102, caption de privacidad en sidebar, ConfigError -> st.error (crear .env desde .env.example), sin chroma_db o vacio -> st.warning `python ingest.py`, avatar isotipo, spinner, expander "Fuentes" solo con fuentes, excepcion inesperada -> mensaje amigable. cache_resource para coleccion y llm.
Pendiente: tema .streamlit/config.toml (Fase 7) y verificacion manual (Fase 8).

## Batch 7 - Fase 7 (7.1-7.3 completas, 7.4 parcial)

Creado: .streamlit/config.toml (base light, primary #7F07C5, bg #FFFFFF, secondaryBg #F7F4FA, text #1F1F1F), tests/test_branding.py (2: tema via regex, sin tomllib; assets existen). Modificado: rag/config.py (DEFAULT_MODEL), .env.example (modelo + fallbacks como comentarios, sin key).

TDD: 7.2 RED -> test_tema_flock_configurado fallo (FileNotFoundError, config.toml ausente); 7.1 GREEN -> 2 passed. Suite: 70 passed.

7.3 modelo (npm install + `npx tsx search-models.ts ":free"`, 15 modelos :free hoy). El provisorio llama-3.3-70b-instruct:free YA NO EXISTE en el listado.
- Default: `google/gemma-4-31b-it:free` (denso 31B instruct, 262k ctx, sin expiration_date, familia Gemma buena en espanol, sigue instrucciones sin "razonamiento" extra que ensucie la respuesta).
- Fallback 1: `google/gemma-4-26b-a4b-it:free` (MoE, 262k, sin expiracion; mismo provider/familia, mas rapido).
- Fallback 2: `nvidia/nemotron-3-super-120b-a12b:free` (120B MoE, 262k, sin expiracion; modelo grande de otra familia por si Google tiene rate limit).
- Descartados: poolside laguna (coding, vencen 2026-10-31), dots-3-note (vence 2026-12-31), liquid lfm 2.6B (muy chico), cohere north-mini-code (coding), nemotron-3-ultra/inkling (grandes pero de razonamiento/multimodales).
Test de config solo exige modelo no vacio, no se pinneo el default viejo.
Riesgo: ids/disponibilidad de :free cambian; verificar con la key real.

7.4: contraste revisado en app.py: #FF5102 solo aparece como extremo del gradiente del header, con texto blanco 1.5rem bold (texto grande, aceptable); nunca texto chico blanco sobre naranja. `.env` NO creado (pendiente del usuario).

## Batch 8 - Fase 8 (parte automatizable)

- 8.1 `.venv/bin/pytest`: 70 passed, offline.
- 8.2 `.venv/bin/python ingest.py` real (descargo ONNX all-MiniLM-L6-v2 ~79MB): "Indexados 38 chunks" en run 1 y run 2 (idempotente). Conteo real 38 (el ~45 de la tarea era estimado).
- 8.3 streamlit headless puerto 8599: /_stcore/health -> "ok", log sin excepciones (solo warning urllib3/LibreSSL y aviso watchdog); proceso detenido. El script no corre sin sesion de navegador, asi que se uso `streamlit.testing.v1.AppTest`: sin key -> st.error "Falta OPENROUTER_API_KEY... Creá un archivo .env..." sin excepcion; con key dummy -> sin excepciones ni warnings, 1 chat_input. Pendiente: revision visual (tema, logos).
- Retrieval sanity sin LLM (top-4, k=4): las 5 preguntas traen la seccion relevante (tabla en el reporte); el riesgo del embedding ingles no se manifiesta en este set. Script en scratchpad, no en repo.
- 8.4, 8.5 pendientes (API key). 8.6: input vacio e indice ausente cubiertos por tests unitarios (is_blank/submit_question/index_ready); key invalida pendiente.

## Batch 9 - Fixes post-verify (W1, W2, W3, W5, S1, S2, S5)

Cambios:
- W1: `TOP_K` default 4 -> 6 (rag/config.py, .env.example, CLAUDE.md, design.md). El embedding NO se cambio (decision del usuario; torch ~1GB). Es una mejora parcial: los chunks intro de Etapa 1/Etapa 3 y Paso 3 siguen fuera del top-8 por el embedding ingles.
- W2: `rag/store.open_collection` devuelve `None` si la coleccion no existe. `app.py` cachea solo el cliente (`get_client`) y abre la coleccion en cada run, asi `python ingest.py` con Streamlit levantado funciona sin reiniciar.
- W5: `test_prompt_enviado_contiene_regla_no_se_y_la_pregunta` ahora asserta `res.text == NO_SE` y `res.sources == []`.
- S2: `app.py` e `ingest.py` resuelven assets/docs/chroma_db relativo a `__file__` (`BASE_DIR`); `app.py` carga `.env` desde `BASE_DIR`.
- Extra: `load_settings` acepta `CHROMA_PATH` en el entorno (override del indice) para poder testear la UI sin tocar el indice real.
- S1: `tests/test_app.py` (2 AppTest offline): sin key -> st.error sin excepcion; key dummy sin indice -> st.warning con `python ingest.py`. Aislan el entorno con monkeypatch (las env vars ganan sobre un .env real).
- S5: openspec/config.yaml (pytest 8.4.2, `.venv/bin/pytest`, capas disponibles); design.md "~45 chunks" -> 38.

Desvio de TDD (honesto): los 2 AppTest se escribieron junto con la implementacion de app.py/CHROMA_PATH y pasaron en el primer run (tests de caracterizacion sobre comportamiento existente); el RED de CHROMA_PATH si se vio fallar antes del GREEN.

Resultado: `.venv/bin/pytest` -> 76 passed. `.venv/bin/python ingest.py` -> 38 chunks.

## TDD Cycle Evidence

| Tarea | Archivo de test | RED (evidencia) | GREEN | REFACTOR |
|-------|-----------------|-----------------|-------|----------|
| 2.1/2.2 config | tests/test_config.py | ModuleNotFoundError rag.config | 6 passed | - |
| 2.3/2.4 chunking | tests/test_chunking.py | ModuleNotFoundError rag.chunking | 20 passed (acum.) | - |
| 2.5 fixture real | tests/test_chunking_proceso.py | ModuleNotFoundError (junto a 2.3) | pasa sin ajustes | 2.6 guard _MIN_BUDGET=50 |
| 3.1/3.2 store | tests/test_store.py | ModuleNotFoundError rag.store | 6 passed (tras corregir nombre de coleccion en el test) | - |
| 3.3/3.4 ingest | tests/test_ingest.py | ModuleNotFoundError ingest | 31 passed (acum.) | 3.5 sin cambios |
| 4.1/4.2 retrieval | tests/test_retrieval.py | ModuleNotFoundError rag.retrieval | 3 passed (+1 integracion = 4) | - |
| 4.3/4.4 prompting | tests/test_prompting.py | ModuleNotFoundError rag.prompting | 40 passed (41 con integracion) | 4.5 sin cambios |
| 5.1/5.2 llm | tests/test_llm.py | ImportError rag.llm | 11 passed | - |
| 5.3/5.4 pipeline | tests/test_pipeline.py | ModuleNotFoundError rag.pipeline | 57 passed (acum.) | 5.5 sin cambios |
| 6.1/6.2 ui_helpers | tests/test_ui_helpers.py | ModuleNotFoundError rag.ui_helpers | 68 passed (acum.) | 6.4 render reutilizado |
| 6.3 app.py | (manual / py_compile) | n/a | n/a | - |
| 7.1/7.2 branding | tests/test_branding.py | FileNotFoundError (config.toml ausente) | 70 passed (acum.) | - |
| 9 W1 TOP_K=6 | tests/test_config.py::test_defaults | AssertionError `4 == 6` | pasa | - |
| 9 W2 open_collection None + re-ingesta | tests/test_store.py (2 nuevos) | NotFoundError al abrir inexistente (test None); el test de re-ingesta pasa como regresion | pasan | - |
| 9 S2 rutas absolutas | tests/test_ingest.py::test_rutas_por_defecto_... | AssertionError (rutas relativas) | pasa | - |
| 9 CHROMA_PATH | tests/test_config.py::test_chroma_path_... | AssertionError (ignoraba el env) | pasa | - |
| 9 W5 aserto Answer.text | tests/test_pipeline.py | n/a (refuerzo de aserto; codigo ya correcto) | pasa | - |
| 9 S1 AppTest | tests/test_app.py (2) | no observado (caracterizacion) | 76 passed | - |


## Batch 10: UX de respuestas

Feedback de usuarios: respuestas largas, fuentes visibles, citas [n].
- rag/prompting.py: nuevo SYSTEM_PROMPT (breve, voseo, sin fuentes ni citas, grounding intacto); NO_SE reescrito (sin "documentacion", con people@flockit.com.ar); contexto rotulado "Tema: <seccion>" bajo "INFORMACIÓN:" (sin [n] ni archivo).
- rag/pipeline.py: `strip_citations` (regex) aplicado al texto; Answer.sources se mantiene interno.
- rag/ui_helpers.py: eliminados format_source/format_sources; mensajes guardan solo role/content.
- app.py: sin expander "Fuentes"; spinner "Pensando...".
- Specs (rag-query, chat-ui) y design.md actualizados.

| Tarea | Archivo de test | RED | GREEN | REFACTOR |
|-------|-----------------|-----|-------|----------|
| 10 prompt (grounding, NO_SE, sin citas/fuentes, brevedad, contexto sin archivo) | tests/test_prompting.py | tests nuevos fallaban (ImportError/asserts) antes de cambiar el prompt | pasan | - |
| 10 strip_citations + integracion + app sin Fuentes | tests/test_pipeline.py | ImportError strip_citations | pasan | - |
| 10 ui_helpers sin fuentes | tests/test_ui_helpers.py | (tests de format_sources eliminados; submit/append sin sources) | pasan | codigo muerto borrado |

Resultado: `.venv/bin/pytest` -> 77 passed.
