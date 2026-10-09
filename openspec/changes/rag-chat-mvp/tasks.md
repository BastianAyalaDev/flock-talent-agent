# Tareas: rag-chat-mvp

Strict TDD: cada módulo testeable va RED (test falla) -> GREEN (mínimo código) -> REFACTOR. Sin red en tests. Nunca hacer build tras cambios. Sin LangChain/LangGraph.
Leyenda: [P] = paralelizable con sus hermanas de la fase; el resto es secuencial. Refs: KI = knowledge-ingestion, RQ = rag-query, UI = chat-ui.

## Fase 1: Scaffold e infraestructura (batch 1)

- [x] 1.1 Crear `requirements.txt` con versiones fijadas: chromadb, openai, python-dotenv, streamlit, pytest (verificar versiones con `pip index versions` o instalar y `pip freeze`). (RQ Sin red en tests)
- [x] 1.2 [P] Crear `.gitignore` (`.env`, `chroma_db/`, `__pycache__/`, `.venv/`, `.pytest_cache/`).
- [x] 1.3 [P] Crear `.env.example` (`OPENROUTER_API_KEY=`, `OPENROUTER_MODEL=`, `TOP_K=4`).
- [x] 1.4 [P] Copiar `flock-logo-color.png` y `flock-isotipo.png` desde `.claude/skills/flock-brand-design/assets/` a `assets/`. (UI Assets de marca)
- [x] 1.5 Crear `rag/__init__.py` (vacío), `tests/__init__.py` o `tests/conftest.py` mínimo, y `pytest.ini` (`testpaths = tests`, `pythonpath = .`).
- [x] 1.6 Crear venv (`python3 -m venv .venv`, `source .venv/bin/activate`, `pip install -r requirements.txt`) y documentar los comandos en un README breve o comentario en `requirements.txt`. Confirmar `pytest` colecta 0 tests sin error.

## Fase 2: Config y chunking (batch 2)

- [x] 2.1 RED: `tests/test_config.py` -- `load_settings` lee key/model/top_k de env; `ConfigError` en español si falta `OPENROUTER_API_KEY`; defaults (`top_k=4`, `chroma_path`, `collection="gestion_talento"`, `history_turns=3`). Usar `monkeypatch` y evitar que dotenv pise el entorno. (RQ Falta la clave, Configuración por env)
- [x] 2.2 GREEN: `rag/config.py` (`Settings`, `ConfigError`, `load_settings` con dotenv).
- [x] 2.3 RED: `tests/test_chunking.py` -- escenarios sintéticos: división por headings `##`, subsección `###` con ruta `A > A1`, fallback por tamaño (ningún chunk > `max_chars`, ruta repetida), texto previo al primer `##` (sección = H1), chunks vacíos descartados, IDs `"{source}::{i:03d}"`, tabla sin cortar. (KI Chunking, KI Metadata)
- [x] 2.4 GREEN: `rag/chunking.py` (`Chunk`, `chunk_markdown`) siguiendo reglas del diseño; el texto del chunk = `"{ruta}\n\n{cuerpo}"`.
- [x] 2.5 RED/GREEN: test con fixture real `docs/proceso.md` (todos los chunks no vacíos, <= 1500 chars, source `proceso.md`, sección con "Comité" presente, IDs únicos). Ajustar chunking si falla.
- [x] 2.6 REFACTOR: limpiar `chunking.py` y `config.py`, tests en verde.

## Fase 3: Store e ingesta (batch 3)

- [x] 3.1 RED: `tests/test_store.py` -- con `chromadb.EphemeralClient()` + EF fake determinístico: `rebuild_collection` devuelve el conteo, guarda metadata `source`/`section`/`heading`/`chunk_index`, ejecutarlo 2 veces no duplica, colección previa con `old.md` desaparece, rebuild sobre colección inexistente no falla. (KI Idempotente, Doc eliminado, Metadata presente)
- [x] 3.2 GREEN: `rag/store.py` (`embedding_function()` único punto de cambio, `rebuild_collection`, `open_collection`).
- [x] 3.3 RED: `tests/test_ingest.py` -- `read_docs(dir)` devuelve solo `.md` (ignora `image.png`); directorio sin `.md` lanza error claro en español; `run_ingest(docs_dir, client, ef)` con fake inyectado recibe documents/metadatas/ids sin red. Usar `tmp_path`. (KI Solo markdown, Directorio sin markdown, Ingesta con fake)
- [x] 3.4 GREEN: `ingest.py` con funciones `read_docs`, `run_ingest` (inyectables) y `main()` CLI delgado (`PersistentClient("./chroma_db")`, imprime conteo). `main` fuera de test.
- [x] 3.5 REFACTOR de store/ingest; suite verde.

## Fase 4: Retrieval y prompting (batch 4)

- [x] 4.1 RED: `tests/test_retrieval.py` -- `FakeCollection.query` con forma Chroma: devuelve k resultados con source/section/distance en orden; colección vacía -> `[]` sin excepción. (RQ Devuelve k resultados, Colección vacía)
- [x] 4.2 GREEN: `rag/retrieval.py` (`RetrievedChunk`, `retrieve`).
- [x] 4.3 [P] RED: `tests/test_prompting.py` -- system prompt contiene reglas (solo contexto, español, frase exacta "No sé: ...", citar `[n]`); mensaje final con `CONTEXTO:` numerado `[n] (archivo — sección)` + `PREGUNTA:`; recorte a `max_turns` turnos (6 mensajes) sin contexto previo; sin chunks -> indica "no hay contexto" y mantiene regla "no sé". (RQ Prompt completo, Sin contexto)
- [x] 4.4 GREEN: `rag/prompting.py` (`build_messages`).
- [x] 4.5 REFACTOR; suite verde.

## Fase 5: LLM y pipeline (batch 5)

- [x] 5.1 RED: `tests/test_llm.py` -- fake client: `make_llm` usa el modelo dado y devuelve el texto; excepciones `openai.RateLimitError` (429), `AuthenticationError`, `APIConnectionError`/`APITimeoutError`, `APIStatusError` y respuesta vacía -> `LLMError` con los mensajes amigables del diseño; test de que `make_llm` sin `client` construye `OpenAI(base_url="https://openrouter.ai/api/v1", api_key=...)` (monkeypatch de la clase, sin red). Construir excepciones con `httpx.Response/Request`. (RQ Cliente OpenRouter, Manejo de errores)
- [x] 5.2 GREEN: `rag/llm.py` (`LLMError`, `LLM`, `make_llm`).
- [x] 5.3 RED: `tests/test_pipeline.py` -- fake collection (2 chunks) + `llm=lambda m: "Respuesta"` -> `Answer.text == "Respuesta"` y fuentes únicas sin duplicados; pregunta fuera de contexto: el prompt enviado al fake contiene la regla "no sé"; LLM que lanza `LLMError` -> mensaje amigable en español, `sources == []`, sin propagar traza; el historial se recorta. (RQ Respuesta con fuentes, Pregunta fuera de contexto, LLM falla, Suite offline)
- [x] 5.4 GREEN: `rag/pipeline.py` (`Answer`, `answer`): retrieve -> build_messages -> llm; captura `LLMError`.
- [x] 5.5 REFACTOR; ejecutar `pytest` completo (debe pasar offline).

## Fase 6: Helpers de UI y app (batch 6)

- [x] 6.1 RED: `tests/test_ui_helpers.py` (puro, sin streamlit) -- `format_source(source, section)` / `format_sources(list)` devuelve cadena legible con archivo y sección; lista vacía -> `""`/None (sin bloque vacío); `is_blank(text)` / `append_turn(history, ...)` ignora entrada vacía o espacios; `append` guarda fuentes con el mensaje; historial persistente en orden; `to_llm_history` excluye fuentes. (UI Formateo de fuentes, Entrada vacía, Mensaje nuevo, Persistencia, Respuesta sin fuentes)
- [x] 6.2 GREEN: `rag/ui_helpers.py` (o `ui_logic.py`) con las funciones puras.
- [x] 6.3 Escribir `app.py` (verificación manual, sin tests): `st.set_page_config` con isotipo, `st.logo`, header con gradiente `#44016B -> #FF5102` (acento solo decorativo), `st.session_state.messages`, `st.chat_input` con placeholder en español, `st.chat_message` con avatar isotipo para assistant, `st.spinner`, expander "Fuentes" solo si hay fuentes, `st.error` ante `ConfigError`/`LLMError`, aviso si `chroma_db` no existe o está vacío ("Ejecutá `python ingest.py`"), advertencia de privacidad de modelos `:free`. Cablear `load_settings`, `open_collection`, `make_llm` con `st.cache_resource`. (UI Chat con historial, Fuentes visibles, Estado de carga, Índice inexistente, Idioma)
- [x] 6.4 REFACTOR: mover lógica residual de `app.py` a helpers si es testeable; suite verde.

## Fase 7: Theming y modelo (batch 7)

- [x] 7.1 Crear `.streamlit/config.toml` con `primaryColor="#7F07C5"`, `backgroundColor="#FFFFFF"`, `secondaryBackgroundColor="#F7F4FA"`, `textColor="#1F1F1F"`. (UI Tema configurado)
- [x] 7.2 [P] Test ligero opcional `tests/test_branding.py`: parsea `config.toml` (`tomllib`) y verifica `primaryColor`; verifica que existan los 2 logos en `assets/`. (UI Tema configurado, Assets de marca) -- si se escribe, ir RED antes de 7.1.
- [x] 7.3 [P] Elegir `OPENROUTER_MODEL` default `:free` con el skill `openrouter-models` (`npm install` en `.claude/skills/openrouter-models/scripts`, correr sus scripts) y reflejarlo como ejemplo en `.env.example`. Cerrar pregunta abierta del diseño.
- [ ] 7.4 Crear `.env` local (gitignored) con la API key real; revisar contraste del acento `#FF5102` (texto blanco solo grande/negrita). (parcial: contraste del acento revisado OK en app.py; pendiente: crear `.env` con la API key real, requiere API key del usuario)

## Fase 8: Verificación manual (demo)

- [x] 8.1 `pytest` completo, sin red: todo verde.
- [x] 8.2 `python ingest.py` (pre-descarga ONNX): indexa todos los `docs/*.md`; re-ejecutar y confirmar mismo conteo (~45 chunks; real: 38). (KI Re-ejecución sin duplicados)
- [x] 8.3 `streamlit run app.py`: verificar tema/logos Flock, textos en español, advertencia de privacidad. (automatizado: health ok + AppTest; pendiente revision visual en navegador)
- [ ] 8.4 Preguntar 3-5 cosas reales sobre `docs/proceso.md` (p. ej. pasos del F360, qué es el Talent Review, rol del Comité, Espacio Champion, buenas prácticas): respuestas en español, con `[n]` y expander "Fuentes" correcto. (pendiente: requiere API key del usuario)
- [ ] 8.5 Pregunta fuera de alcance (p. ej. "¿Cuál es la capital de Francia?"): responde "No sé: no encuentro esa información en la documentación." y sin bloque de fuentes vacío. (RQ Pregunta fuera de contexto) (pendiente: requiere API key del usuario)
- [ ] 8.6 Casos de borde: input vacío no envía; app sin `chroma_db` muestra aviso; key inválida muestra error amigable sin traza. Anotar problemas de retrieval en español (embedding inglés) y ajustar `TOP_K` si hace falta. (parcial: input vacio e indice ausente cubiertos por tests unitarios test_ui_helpers; pendiente: key invalida con API key del usuario)

## Resumen

8 fases, 41 tareas. Orden estricto por dependencia: config -> chunking -> store -> ingest -> retrieval -> prompting -> llm -> pipeline -> ui helpers -> app -> theming -> demo. Paralelismo solo dentro de Fase 1 (1.2-1.4), 4.3 (prompting independiente de retrieval), y 7.2/7.3.
