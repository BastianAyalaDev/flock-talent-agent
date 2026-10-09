"""UI Streamlit del agente de Gestion de Talento (capa delgada; la logica vive en rag/)."""
from __future__ import annotations

import os

import chromadb
import streamlit as st

from rag.config import ConfigError, load_settings
from rag.llm import make_llm
from rag.pipeline import Answer, answer
from rag.store import open_collection
from rag.ui_helpers import index_ready, submit_question

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ISOTIPO = os.path.join(BASE_DIR, "assets", "flock-isotipo.png")
LOGO = os.path.join(BASE_DIR, "assets", "flock-logo-color.png")

TEMAS = """
**¿Sobre qué podés preguntarme?**

- **Sobre Flock:** qué hace la empresa, su historia, oficinas, valores, servicios, productos propios y clientes.
- **Gestión de Talento:** cómo funciona el Feedback 360, la Talent Review y el Comité, y en qué meses ocurre cada etapa.
- **Roles:** qué hace un champion, un championee, People, los referentes y el Comité.
- **Objetivos y crecimiento:** cómo definir objetivos SMART, los playbooks, las instancias y cómo se presenta un caso para promoción.
- **Guía para champions:** qué se espera del rol, qué hacer con un nuevo championee y buenas prácticas.
- **PIbot:** qué comando de Slack usar para pedir, dar o ver feedback, consultar tu playbook y más.
- **Recursos:** templates, el generador de informes y dónde encontrar cada cosa.
"""

EJEMPLOS = """
**Por ejemplo:**
- ¿Qué tengo que hacer cuando me toca el Feedback 360?
- ¿Cómo le doy feedback a un compañero?
- ¿Cuántas veces al año puedo presentar mi caso al Comité?
- ¿Cuáles son los valores de Flock?
"""

st.set_page_config(page_title="Asistente Flock", page_icon=ISOTIPO)
st.logo(LOGO, icon_image=ISOTIPO)

st.markdown(
    """
    <style>
    .flock-header {
        background: linear-gradient(90deg, #44016B 0%, #FF5102 100%);
        color: #FFFFFF;
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    </style>
    <div class="flock-header">Asistente Flock</div>
    """,
    unsafe_allow_html=True,
)
st.caption("Tu guía para entender cómo funcionan las cosas en Flock.")

with st.sidebar:
    st.markdown(TEMAS)
    st.divider()
    st.caption(
        "Privacidad: los modelos gratuitos de OpenRouter pueden registrar los prompts. "
        "Evitá escribir datos personales o confidenciales."
    )

try:
    settings = load_settings(os.path.join(BASE_DIR, ".env"))
except ConfigError as exc:
    st.error(
        "%s Creá un archivo `.env` a partir de `.env.example` y completá tu clave." % exc
    )
    st.stop()


@st.cache_resource
def get_client(path: str):
    # Se cachea solo el cliente. La coleccion se abre en cada run: `python ingest.py`
    # la recrea con un id nuevo y un handle cacheado quedaria obsoleto (NotFoundError).
    return chromadb.PersistentClient(path=path)


@st.cache_resource
def get_llm(api_key: str, model: str):
    return make_llm(api_key, model)


chroma_path = os.path.join(BASE_DIR, settings.chroma_path)  # absoluto se respeta tal cual
collection = None
if os.path.isdir(chroma_path):
    try:
        collection = open_collection(get_client(chroma_path), settings.collection)
    except Exception:
        collection = None

if not index_ready(collection):
    st.warning(
        "Todavía no hay un índice de documentos. Ejecutá `python ingest.py` y recargá la página."
    )
    st.stop()

llm = get_llm(settings.api_key, settings.model)

if "messages" not in st.session_state:
    st.session_state.messages = []


def render_message(message):
    avatar = ISOTIPO if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


if not st.session_state.messages:
    with st.chat_message("assistant", avatar=ISOTIPO):
        st.markdown("¡Hola! Soy el asistente de Flock. " + TEMAS + EJEMPLOS)

for msg in st.session_state.messages:
    render_message(msg)

prompt = st.chat_input("Escribí tu pregunta sobre Flock")
if prompt and prompt.strip():
    with st.chat_message("user"):
        st.markdown(prompt.strip())

    def answer_fn(question, prior_history):
        try:
            return answer(
                question,
                prior_history,
                collection,
                llm,
                k=settings.top_k,
                max_turns=settings.history_turns,
            )
        except Exception:
            return Answer(text="Ocurrió un error inesperado. Intentá de nuevo.", sources=[])

    with st.spinner("Pensando..."):
        submit_question(st.session_state.messages, prompt, answer_fn)
    render_message(st.session_state.messages[-1])
