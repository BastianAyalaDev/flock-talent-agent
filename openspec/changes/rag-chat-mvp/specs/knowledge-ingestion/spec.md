# Especificación Delta: knowledge-ingestion

Capacidad NUEVA. Convierte `docs/*.md` en un índice Chroma local con metadata.

## ADDED Requirements

### Requirement: Lectura de documentos
El sistema MUST leer todos los archivos `docs/*.md` y MUST NOT indexar otros formatos (p. ej. `docs/image.png`).

#### Scenario: Solo markdown
- GIVEN un directorio docs con `a.md`, `b.md` e `image.png`
- WHEN se ejecuta la lectura de documentos
- THEN se devuelven exactamente los contenidos de `a.md` y `b.md`

#### Scenario: Directorio sin markdown
- GIVEN un directorio docs sin archivos `.md`
- WHEN se ejecuta la ingesta
- THEN falla con un mensaje claro en español y no crea chunks

### Requirement: Chunking por headings
El sistema MUST dividir cada documento en chunks por headings `##` y `###`. Si un chunk excede un tamaño máximo configurable, MUST subdividirlo por tamaño (fallback). Cada chunk MUST incluir el título de su sección en el texto y MUST NOT ser vacío.

#### Scenario: División por headings
- GIVEN un markdown con dos secciones `## A` y `## B`
- WHEN se hace chunking
- THEN resultan al menos dos chunks, uno por sección, cada uno con su heading

#### Scenario: Subsección anidada
- GIVEN una sección `## A` con subsección `### A1`
- WHEN se hace chunking
- THEN el chunk de `A1` queda identificado con la sección `A1` (o `A > A1`)

#### Scenario: Fallback por tamaño
- GIVEN una sección cuyo texto supera el tamaño máximo
- WHEN se hace chunking
- THEN se parte en varios chunks, ninguno mayor al máximo, conservando el heading de origen

#### Scenario: Texto previo al primer heading
- GIVEN un documento con texto antes del primer `##`
- WHEN se hace chunking
- THEN ese texto se incluye en un chunk (no se pierde)

### Requirement: Metadata de chunks
Cada chunk MUST almacenarse con metadata `source` (nombre de archivo) y `section` (heading).

#### Scenario: Metadata presente
- GIVEN un chunk de `proceso.md` bajo `## Comité`
- WHEN se indexa
- THEN su metadata contiene `source="proceso.md"` y `section` con "Comité"

### Requirement: Indexado idempotente
La ingesta MUST reconstruir la colección desde cero en cada ejecución, persistiendo en `./chroma_db`. Ejecutarla N veces sobre los mismos docs MUST producir el mismo número de chunks. Los IDs MUST ser determinísticos.

#### Scenario: Re-ejecución sin duplicados
- GIVEN una colección (fake) ya poblada con los chunks de los docs
- WHEN se ejecuta la ingesta otra vez
- THEN la cantidad de chunks es igual a la de la primera corrida

#### Scenario: Doc eliminado
- GIVEN un índice previo que contenía `old.md`, ya borrado de docs
- WHEN se ejecuta la ingesta
- THEN ningún chunk con `source="old.md"` permanece

### Requirement: Testabilidad sin red
La ingesta MUST recibir la colección/cliente Chroma por inyección para poder probarse con un fake, sin descargar modelos ni usar red.

#### Scenario: Ingesta con fake
- GIVEN una colección fake inyectada y docs temporales
- WHEN se ejecuta la ingesta
- THEN el fake recibe documentos, metadatas e ids, sin acceso a red
