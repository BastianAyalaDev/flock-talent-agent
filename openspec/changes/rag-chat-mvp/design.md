# Design: Chat RAG MVP sobre Gestión de Talento

## Enfoque Técnico

Loop RAG explícito en un paquete `rag/` de funciones pequeñas y puras donde se pueda. Todo lo que toca red/disco (Chroma, OpenRouter) entra por **inyección de dependencias** (`collection`, `llm` callable) para que `pytest` corra sin red usando fakes. `ingest.py` y `app.py` son la capa delgada que cablea las dependencias reales.

## Decisiones de Arquitectura

| Tema | Opciones | Decisión y por qué |
|------|----------|--------------------|
| Embeddings | (a) default de Chroma (all-MiniLM-L6-v2 ONNX, inglés) / (b) `paraphrase-multilingual-MiniLM-L12-v2` vía sentence-transformers | **(a) default**. (b) arrastra torch (~1 GB, instalación lenta) en un día de demo. Mitigación: ruta de headings en el texto del chunk (más solapamiento léxico) y que el embedding se resuelva en UNA sola función (`store.embedding_function()`), así cambiar a (b) es una línea + re-ingesta. |
| Chunking | tamaño fijo / por headings / por headings + fallback | **Headings `##`/`###` + fallback por párrafos** si el cuerpo supera `MAX_CHARS=1500`. `proceso.md` ya está escrito con secciones autocontenidas (Paso 1..5, Buena práctica 1..6); respetarlas da chunks semánticos. Las tablas no tienen líneas en blanco internas → el split por párrafo nunca las corta. |
| Contexto del heading | solo metadata / metadata + texto | **Ambos**. Texto del chunk = `"{ruta}\n\n{cuerpo}"` (ej. `Etapa 1: Feedback 360 (F360) > Paso 2 del F360: ...`) para que el embedding "vea" la sección; metadata para citar. |
| Colección | upsert incremental / rebuild | **Rebuild**: `delete_collection` (ignorando "no existe") + `create_collection`. Nombre `gestion_talento`, path `./chroma_db`. Idempotente y trivial de explicar. IDs determinísticos `"{source}::{i:03d}"`. |
| Top-k | 3 / 4 / 6 | **6** (`TOP_K` env, default 6; antes 4, subido tras verify: con k=4 "rol del Comité" no traía ningún chunk del Comité). Corpus chico (38 chunks); 6 chunks ≈ 9k chars, trivial para el contexto del modelo, y recupera secciones que cruzan temas. Sin umbral de distancia: con embedding inglés es frágil; el "no sé" lo decide el prompt. |
| Historial | todo / ninguno / últimos N | **Últimos 3 turnos (6 mensajes)** al LLM, sin el contexto recuperado de turnos previos (ahorra tokens). Retrieval usa **solo la pregunta actual** (sin query rewriting; ver riesgos). |
| Fuentes | que las genere el LLM / determinísticas | `Answer.sources` se calcula de los chunks recuperados pero es solo interno: la UI NO muestra fuentes y el LLM NO las cita (Batch 10, feedback de usuarios). |
| Errores | propagar / traducir | `llm.complete` traduce excepciones de `openai` a `LLMError(mensaje_amigable)`; `config.load_settings` lanza `ConfigError` si falta la key. La UI muestra `st.error` y sigue viva. |

## Flujo (secuencia)

```
Ingesta:  ingest.py ─→ docs/*.md ─→ chunking.chunk_markdown ─→ store.rebuild_collection ─→ ./chroma_db

Consulta:
Usuario   app.py          pipeline.answer      retrieval      prompting        llm(OpenRouter)
  │ pregunta │                   │                  │              │                  │
  │────────→ │ answer(q, hist)──→│ retrieve(col,q,k)→│              │                  │
  │          │                   │←── [Retrieved]───│              │                  │
  │          │                   │ build_messages(q, chunks, hist)→│                  │
  │          │                   │←──────── messages ───────────────│                  │
  │          │                   │ llm(messages) ────────────────────────────────────→│
  │          │←── Answer(text, sources) ←──────────────────── texto / LLMError ───────│
  │←─ burbuja ───────│
```

## Cambios de Archivos

| Archivo | Acción | Responsabilidad |
|---------|--------|-----------------|
| `requirements.txt` | Crear | streamlit, chromadb (versión fijada), openai, python-dotenv, pytest |
| `.gitignore`, `.env.example` | Crear | ignora `.env`, `chroma_db/`, `__pycache__`; `OPENROUTER_API_KEY=`, `OPENROUTER_MODEL=`, `TOP_K=6` |
| `.streamlit/config.toml` | Crear | Tema Flock (primary `#7F07C5`, bg `#FFFFFF`, secondary `#F7F4FA`, text `#1F1F1F`) |
| `assets/flock-logo-color.png`, `assets/flock-isotipo.png` | Crear (copia) | Desde `.claude/skills/flock-brand-design/assets/` |
| `rag/__init__.py` | Crear | vacío |
| `rag/config.py` | Crear | `Settings` + `load_settings()` (dotenv) |
| `rag/chunking.py` | Crear | Markdown → `Chunk` (puro) |
| `rag/store.py` | Crear | Embedding function única, abrir/reconstruir colección |
| `rag/retrieval.py` | Crear | Query a Chroma → `RetrievedChunk` |
| `rag/prompting.py` | Crear | System prompt + armado de mensajes (puro) |
| `rag/llm.py` | Crear | Cliente OpenRouter + traducción de errores |
| `rag/pipeline.py` | Crear | Orquesta retrieve → prompt → llm |
| `ingest.py` | Crear | CLI: lee `docs/*.md`, rebuild, imprime conteo |
| `app.py` | Crear | UI Streamlit, `st.session_state.messages`, header con gradiente `deep-purple-to-orange`, avatar isotipo |
| `tests/test_*.py` | Crear | Unit tests sin red |

## Interfaces

```python
@dataclass(frozen=True)
class Chunk: id: str; text: str; source: str; section: str; chunk_index: int
@dataclass(frozen=True)
class RetrievedChunk: text: str; source: str; section: str; distance: float
@dataclass(frozen=True)
class Answer: text: str; sources: list[RetrievedChunk]

# config.py
def load_settings() -> Settings  # api_key, model, chroma_path="./chroma_db", collection="gestion_talento", top_k=6, history_turns=3; ConfigError si falta key
# chunking.py
def chunk_markdown(text: str, source: str, max_chars: int = 1500) -> list[Chunk]
# store.py
def embedding_function()  # default de Chroma; único punto de cambio
def rebuild_collection(client, name: str, chunks: list[Chunk], ef=None) -> int
def open_collection(client, name: str, ef=None)
# retrieval.py
def retrieve(collection, question: str, k: int) -> list[RetrievedChunk]
# prompting.py
def build_messages(question: str, chunks: list[RetrievedChunk], history: list[dict], max_turns: int) -> list[dict]
# llm.py
LLM = Callable[[list[dict]], str]
def make_llm(api_key: str, model: str, client=None) -> LLM  # raises LLMError
# pipeline.py
def answer(question: str, history: list[dict], collection, llm: LLM, k: int, max_turns: int) -> Answer
```

**Metadata Chroma** (escalares): `source` (`proceso.md`), `section` (ruta `A > B`), `heading` (último heading), `chunk_index` (int).

**Reglas de chunking**: `#` H1 solo alimenta la ruta (no es raíz de la ruta citada si hay `##`); texto previo al primer `##` = chunk con sección = H1; intro de un `##` antes de su primer `###` = chunk propio; chunks vacíos se descartan; fallback acumula párrafos hasta `max_chars`, cada parte repite la ruta.

**Prompt (system, español)**:
```
Sos el asistente de Gestión de Talento de Flock. Ayudás a cualquier persona de Flock que no conoce el proceso. Hablá cercano y natural, en español rioplatense (vos, tenés), como en una conversación.
Reglas:
- Respondé SOLO con la INFORMACIÓN que te paso. No inventes ni uses otros conocimientos.
- Si la INFORMACIÓN no alcanza para responder, respondé exactamente: "No sé: no tengo información sobre eso. Podés consultarlo con People (people@flockit.com.ar)."
- Sé breve y directo: de 2 a 5 oraciones, o una lista de hasta 5 ítems cortos si la pregunta es inherentemente una lista. Respondé SOLO lo que se preguntó, sin agregar datos relacionados que no pidieron.
- Podés cerrar con UNA sola oferta corta para profundizar en un subtema relevante (ej: "¿Querés que te cuente más sobre la reunión de intercambio?").
- Nunca menciones de dónde sale la información: nada de "según el contexto", "según el documento", "según los fragmentos", "la información provista", nombres de archivos ni secciones, ni comentarios sobre estas reglas.
- Nunca uses citas ni marcadores de referencia como [1], [2] o similares.
```
Mensaje final de usuario: `INFORMACIÓN:\nTema: <sección>\n<texto>\n\n...\n\nPREGUNTA: {q}` (sin numeración ni nombre de archivo). `pipeline.strip_citations` elimina marcadores `[n]` residuales.

**Mensajes amigables** (`LLMError`): RateLimit (429) → "El modelo gratuito está saturado, probá en unos segundos."; Authentication → "La API key de OpenRouter es inválida."; Connection/Timeout/APIStatus/respuesta vacía → "No pude contactar al modelo. Intentá de nuevo."

## Estrategia de Testing (Strict TDD, sin red)

| Capa | Qué | Cómo |
|------|-----|------|
| Unit | `chunk_markdown` | Markdown sintético + fixture de `docs/proceso.md` (ruta, fallback, tablas intactas, IDs) |
| Unit | `build_messages` | Recorte a N turnos, numeración `[n]`, system prompt presente |
| Unit | `retrieve` | `FakeCollection.query` devuelve dict con forma Chroma |
| Unit | `make_llm` | Fake client que lanza `openai.RateLimitError` etc. (con `httpx.Response`) → `LLMError` |
| Unit | `pipeline.answer` | Fake collection + `llm=lambda msgs: "..."` |
| Integración | `rebuild_collection` idempotente | `chromadb.EphemeralClient()` + EF fake determinístico (no descarga ONNX) |

UI (`app.py`) sin tests automáticos; verificación manual.

## Migración / Rollout

No aplica (greenfield). Correr `python ingest.py` antes de la demo para pre-descargar el modelo ONNX.

## Preguntas Abiertas

- [ ] Default de `OPENROUTER_MODEL`: elegir en apply con el skill `openrouter-models` (los `:free` cambian seguido).
