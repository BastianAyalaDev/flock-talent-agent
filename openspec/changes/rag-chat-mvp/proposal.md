# Propuesta: Chat RAG MVP sobre Gestión de Talento

## Intención

Demo didáctica para el AI Day de Flock IT (lista hoy): un chat que responde preguntas sobre Gestión de Talento (F360, Talent Review, Comité, roles, Espacio Champion, buenas prácticas, recursos) usando SOLO `docs/*.md`, citando fuentes. El loop RAG se escribe a mano (sin LangChain) para que el público vea cada paso.

## Alcance

### Incluido
- Scaffold: `requirements.txt` (con pytest), `.gitignore`, `.env.example`, `.streamlit/config.toml`, `assets/` (logos Flock)
- `ingest.py`: lee todos los `docs/*.md`, chunking por headings `##/###` con fallback por tamaño, metadata (archivo, sección); reconstruye la colección desde cero en cada corrida (idempotente)
- Módulo `rag/`: chunking, retrieval top-k, armado de prompt, cliente LLM (OpenRouter vía `openai` SDK, modelo por `OPENROUTER_MODEL`)
- `app.py`: chat Streamlit con historial en `st.session_state`, respuesta + fuentes, branding Flock
- Tests pytest con fakes para LLM/Chroma

### Excluido
- Auth, deploy, persistencia multiusuario, LangChain/LangGraph, frameworks de evaluación
- Indexar `docs/image.png`
- Streaming (nice-to-have opcional)

## Capacidades

### Nuevas
- `knowledge-ingestion`: lectura de docs, chunking por headings, indexado idempotente en Chroma con metadata
- `rag-query`: retrieval top-k, prompt con reglas (solo contexto, español, "no sé", citar fuentes), llamada al LLM
- `chat-ui`: interfaz Streamlit con historial, fuentes visibles y branding Flock

### Modificadas
- Ninguna

## Enfoque

Loop explícito: chunk → embed (función default local de Chroma) → persistir en `./chroma_db` → query → top-k → prompt → LLM OpenRouter `:free`. Llamadas de red/LLM detrás de funciones pequeñas inyectables para testear con fakes (Strict TDD). Primeras tareas: scaffold + pytest.

## Áreas Afectadas

| Área | Impacto | Descripción |
|------|---------|-------------|
| `requirements.txt`, `.gitignore`, `.env.example` | Nuevo | Scaffold y config |
| `.streamlit/config.toml`, `assets/` | Nuevo | Tema y logos Flock |
| `ingest.py` | Nuevo | CLI de indexado |
| `rag/` | Nuevo | chunking, retrieval, prompting, llm |
| `app.py` | Nuevo | UI de chat |
| `tests/` | Nuevo | Tests unitarios |
| `chroma_db/` | Generado | Índice (gitignored) |

## Riesgos

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| Proveedores free de OpenRouter pueden loguear prompts (datos internos) | Alta | Advertirlo en la demo; modelo configurable por env |
| Rate limits / caída del modelo free | Media | Modelo configurable; mensaje de error amigable |
| Primera descarga del modelo de embeddings (ONNX) lenta/sin red | Media | Correr `ingest.py` antes de la demo |
| Embedding default (inglés) con retrieval débil en español | Media | Headings autocontenidos; top-k ajustable |
| Tiempo (un día) | Alta | Alcance mínimo; streaming opcional |

## Plan de Rollback

Greenfield: borrar archivos nuevos y `chroma_db/`. Índice corrupto → re-ejecutar `python ingest.py`.

## Dependencias

- `OPENROUTER_API_KEY` válida y modelo `:free` disponible
- Paquetes: streamlit, chromadb, openai, python-dotenv, pytest

## Criterios de Éxito

- [ ] `python ingest.py` indexa todos los `docs/*.md`; re-ejecutarlo no duplica chunks
- [ ] `streamlit run app.py` responde en español citando archivo/sección
- [ ] Pregunta fuera del contexto → responde que no sabe
- [ ] UI con paleta y logos Flock
- [ ] `pytest` pasa sin red
