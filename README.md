# Chat RAG - Gestión de Talento (AI Day, Flock IT)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # completar OPENROUTER_API_KEY y OPENROUTER_MODEL
```

## Uso

```bash
python ingest.py          # indexa docs/*.md en ./chroma_db
streamlit run app.py      # levanta el chat
pytest                    # tests (sin red)
```
