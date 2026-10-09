# Especificación Delta: rag-query

Capacidad NUEVA. Loop RAG escrito a mano: retrieval top-k, prompt y LLM. SIN LangChain/LangGraph.

## ADDED Requirements

### Requirement: Retrieval top-k
El sistema MUST consultar la colección con la pregunta y devolver los top-k chunks (k configurable, por defecto 4) con texto y metadata (`source`, `section`), en orden de relevancia.

#### Scenario: Devuelve k resultados
- GIVEN una colección fake con 10 chunks y k=3
- WHEN se recupera contexto para una pregunta
- THEN se devuelven 3 chunks con `source` y `section`

#### Scenario: Colección vacía
- GIVEN una colección fake vacía
- WHEN se recupera contexto
- THEN se devuelve lista vacía sin lanzar excepción

### Requirement: Armado de prompt
El prompt MUST incluir: (a) instrucciones de responder SOLO con la información provista, (b) responder en español rioplatense, cercano y conversacional, (c) responder con la frase NO_SE ("No sé: no tengo información sobre eso. Podés consultarlo con People (people@flockit.com.ar).") si la información no alcanza, (d) ser breve (2-5 oraciones o lista de hasta ~5 ítems) y responder solo lo preguntado, con a lo sumo UNA oferta final de profundizar, (e) NUNCA citar ni mencionar fuentes (sin "según el contexto/documento", sin nombres de archivo, sin marcadores [n], sin comentarios sobre las reglas), (f) los fragmentos recuperados rotulados solo por tema, y (g) la pregunta del usuario. El historial reciente MAY incluirse.

#### Scenario: Prompt completo
- GIVEN dos chunks recuperados y una pregunta
- WHEN se arma el prompt
- THEN el system prompt contiene las reglas (a)-(e) y los mensajes incluyen ambos fragmentos (sin nombre de archivo ni numeración) y la pregunta

#### Scenario: Sin contexto
- GIVEN cero chunks recuperados
- WHEN se arma el prompt
- THEN el prompt indica que no hay contexto disponible y mantiene la regla de "no sé"

### Requirement: Cliente LLM OpenRouter
El cliente MUST usar el SDK `openai` con `base_url=https://openrouter.ai/api/v1`, la clave de `OPENROUTER_API_KEY` y el modelo de `OPENROUTER_MODEL` (configurable por env, modelo `:free`). MUST NOT hardcodear la clave. La llamada MUST ser inyectable para tests.

#### Scenario: Configuración por env
- GIVEN `OPENROUTER_MODEL=foo/bar:free` y una clave en el entorno
- WHEN se construye el cliente
- THEN se usa ese modelo y el base_url de OpenRouter

#### Scenario: Falta la clave
- GIVEN `OPENROUTER_API_KEY` ausente
- WHEN se intenta responder
- THEN se informa un error claro en español indicando configurar la clave

### Requirement: Respuesta breve sin citar fuentes
La función de respuesta MUST devolver el texto del LLM sin marcadores de cita (red de seguridad: se eliminan patrones como `[1]`, `[2, 3]`). El texto MUST NOT mencionar el origen de la información. `Answer.sources` se conserva solo para uso interno; la UI no lo muestra.

#### Scenario: Respuesta con fake
- GIVEN un retriever fake con 2 chunks y un LLM fake que responde "Respuesta"
- WHEN se responde una pregunta
- THEN el resultado contiene "Respuesta" y `sources` interno sin duplicados

#### Scenario: Citas residuales
- GIVEN un LLM fake que responde "Respuesta [1] clara [2, 3]."
- WHEN se responde
- THEN el texto es "Respuesta clara."

#### Scenario: Pregunta fuera de contexto
- GIVEN un contexto no relacionado y un LLM fake que sigue las reglas
- WHEN se responde
- THEN el prompt enviado contiene la regla de "no sé" y se muestra la respuesta del LLM

### Requirement: Manejo de errores del LLM
Ante fallo del LLM (rate limit, timeout, caída) el sistema MUST devolver un mensaje amigable en español y MUST NOT propagar la traza al usuario.

#### Scenario: LLM falla
- GIVEN un LLM fake que lanza excepción
- WHEN se responde una pregunta
- THEN se devuelve un mensaje de error amigable en español y ninguna fuente

### Requirement: Sin red en tests
Todo el flujo MUST poder probarse con fakes de Chroma y LLM; `pytest` MUST pasar sin red.

#### Scenario: Suite offline
- GIVEN fakes inyectados
- WHEN corre `pytest` sin conexión
- THEN todos los tests de rag-query pasan
