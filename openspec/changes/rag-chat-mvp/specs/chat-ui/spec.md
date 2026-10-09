# Especificación Delta: chat-ui

Capacidad NUEVA. Interfaz Streamlit (`app.py`) con branding Flock. La lógica testeable MUST vivir fuera de las llamadas `st.*`.

## ADDED Requirements

### Requirement: Chat con historial
La UI MUST usar `st.chat_input` y `st.chat_message`, y MUST conservar el historial en `st.session_state`, mostrándolo completo en cada rerun.

#### Scenario: Mensaje nuevo
- GIVEN un historial vacío
- WHEN el usuario envía una pregunta
- THEN se agregan al historial el mensaje del usuario y la respuesta del asistente

#### Scenario: Persistencia entre reruns
- GIVEN un historial con 2 turnos
- WHEN la app se re-ejecuta
- THEN los 2 turnos siguen visibles en orden

#### Scenario: Entrada vacía
- GIVEN un input vacío o solo espacios
- WHEN se intenta enviar
- THEN no se agrega ningún mensaje ni se llama al LLM

### Requirement: Sin fuentes visibles
La UI MUST NOT mostrar fuentes (ni expander "Fuentes", ni archivos/secciones) bajo las respuestas; el público no conoce el origen de la información. Los mensajes del historial guardan solo `role` y `content`.

#### Scenario: Respuesta sin bloque de fuentes
- GIVEN una respuesta del asistente
- WHEN se renderiza
- THEN solo se muestra el texto de la respuesta, sin expander ni lista de fuentes

### Requirement: Estado de carga y errores
La UI SHOULD mostrar un indicador de espera mientras se genera la respuesta y MUST mostrar errores como mensajes amigables en español, sin trazas.

#### Scenario: Índice inexistente
- GIVEN que `chroma_db` no existe o está vacío
- WHEN se abre la app
- THEN se muestra un aviso en español indicando ejecutar `python ingest.py`

### Requirement: Branding Flock
La UI MUST seguir la skill flock-brand-design: color primario `#7F07C5`, acento `#FF5102` (solo como acento; texto blanco sobre él solo grande/negrita), superficies oscuras `#44016B`; tema en `.streamlit/config.toml`; `flock-isotipo.png` como ícono de página y avatar del asistente; `flock-logo-color.png` como logo por defecto. Los logos MUST existir en `assets/`.

#### Scenario: Tema configurado
- GIVEN `.streamlit/config.toml`
- WHEN se lee
- THEN `primaryColor` es `#7F07C5`

#### Scenario: Assets de marca
- GIVEN el directorio `assets/`
- WHEN se verifica
- THEN existen `flock-logo-color.png` y `flock-isotipo.png`

### Requirement: Idioma y advertencia de privacidad
Todo el texto de la UI MUST estar en español. La UI SHOULD advertir que los modelos `:free` de OpenRouter pueden registrar los prompts.

#### Scenario: Textos en español
- GIVEN la app renderizada
- WHEN se revisan título, placeholder del input y mensajes
- THEN están en español y se muestra la advertencia de privacidad

### Requirement: Testabilidad
La lógica de historial MUST estar en funciones puras probables con pytest sin red ni Streamlit en ejecución.

#### Scenario: Historial sin fuentes
- GIVEN un turno agregado al historial
- WHEN se inspecciona el mensaje del asistente
- THEN contiene solo `role` y `content`
