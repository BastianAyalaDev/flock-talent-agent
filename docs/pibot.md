# PIbot: la app de Slack de Feedback de Flock

## Qué es PIbot

PIbot (π-bot) es la aplicación interna de Slack que gestiona el Feedback 360 en Flock: "¡Tu solución de Feedback en Flock!". Con PIbot podés solicitar feedback, dar feedback y ver el estado de tus feedbacks pendientes. Antes de pedir feedback, hay que hacer la autorreflexión.

Todos los comandos de PIbot se escriben en Slack. Donde dice `@usuario`, se reemplaza por la mención de la persona en Slack. Lo que aparece entre corchetes, como `[@usuario]`, es opcional: sin usuario, el comando muestra tu propia información.

Instructivo de instalación y uso de PIbot: https://fs-dev.notion.site/PIbot-bot-8babc5b58f7f456cbbbc34e1ee7dc62b

## Lista completa de comandos de PIbot

| Comando | Para qué sirve |
|---------|----------------|
| `/feedback-auto-reflexion` | Completar tu autorreflexión |
| `/feedback-pedir` | Pedir feedback a alguien |
| `/feedback-dar @usuario` | Responder un feedback que te solicitaron |
| `/feedback-status` | Ver el estado de los feedbacks |
| `/feedback-season [@usuario]` | Ver el feedback de temporadas anteriores |
| `/instafeedback @usuario` | Dar instafeedback (feedback espontáneo) a un flocker |
| `/dar-recordatorio` | Enviar recordatorios de feedbacks y autorreflexiones pendientes |
| `/playbook [@usuario]` | Consultar tu playbook e instancia, o los de otra persona |
| `/puesta-punto [@usuario]` | Consultar tu puesta a punto, o la de otra persona |
| `/playbook-status [@usuario]` | Ver el estado de tus puestas a punto y actualizaciones |
| `/carga-puesta-punto @usuario` | Cargar la puesta a punto de un flocker |
| `/actualizacion-instancia @usuario` | Cargar una actualización de instancia de un flocker |
| `/feedback-ayuda` | Ver cómo usar PIbot |

## Comandos de PIbot para el Feedback 360

### Comando de PIbot para hacer la autorreflexión: /feedback-auto-reflexion

`/feedback-auto-reflexion` te permite completar tu autorreflexión. Es el primer paso del Feedback 360: el championee reflexiona sobre sus logros, aprendizajes y áreas de mejora antes de recibir devoluciones.

### Comando de PIbot para pedir feedback: /feedback-pedir

`/feedback-pedir` sirve para pedirle feedback a alguien de Flock. Se usa en el paso 3 del Feedback 360, después de acordar con tu champion la lista de personas. A personas externas (de clientes) el feedback no se pide por PIbot, sino por email con el template "Solicitud Feedback Externos".

### Comando de PIbot para dar o responder un feedback: /feedback-dar

`/feedback-dar @usuario` sirve para responder un feedback que te solicitaron. Si alguien te pidió feedback, lo das con este comando, mencionando a esa persona.

### Comando de PIbot para ver el estado de los feedbacks: /feedback-status

`/feedback-status` muestra el estado de los feedbacks. El champion lo usa como `/feedback-status @nombre` para ver la autorreflexión y los feedbacks recibidos por su championee, por ejemplo para preparar la reunión de intercambio.

### Comando de PIbot para ver feedbacks anteriores o del año pasado: /feedback-season

`/feedback-season [@usuario]` muestra el feedback de temporadas anteriores: los feedbacks que recibiste en ciclos o años pasados (por ejemplo, el feedback del año pasado o del Feedback 360 anterior). Sin usuario, muestra el tuyo.

### Comando de PIbot para enviar recordatorios: /dar-recordatorio

`/dar-recordatorio` envía recordatorios de feedbacks y autorreflexiones pendientes.

## Comando de PIbot para feedback espontáneo: /instafeedback

`/instafeedback @usuario` sirve para dar instafeedback a un flocker: un feedback espontáneo en el día a día, fuera del momento formal del Feedback 360. En Flock se alienta el feedback espontáneo además del Feedback 360.

## Comandos de PIbot para playbook, instancia y puesta a punto

### Comando de PIbot para consultar el playbook y la instancia: /playbook

`/playbook [@usuario]` te muestra tu playbook y la instancia en la que estás. Con `@usuario`, muestra el playbook y la instancia de otra persona.

### Comando de PIbot para consultar la puesta a punto: /puesta-punto

`/puesta-punto [@usuario]` te muestra tu puesta a punto. Con `@usuario`, muestra la de otra persona.

### Comando de PIbot para ver el estado de puestas a punto y actualizaciones: /playbook-status

`/playbook-status [@usuario]` muestra el estado de tus puestas a punto y actualizaciones de instancia. Con `@usuario`, muestra el de otra persona.

### Comando de PIbot para cargar una puesta a punto: /carga-puesta-punto

`/carga-puesta-punto @usuario` sirve para cargar la puesta a punto de un flocker.

### Comando de PIbot para cargar una actualización de instancia: /actualizacion-instancia

`/actualizacion-instancia @usuario` sirve para cargar una actualización de instancia de un flocker, por ejemplo cuando cambia su instancia en el playbook.

## Comando de PIbot para pedir ayuda: /feedback-ayuda

`/feedback-ayuda` explica cómo usar PIbot. Si no sabés qué comando usar, empezá por este o consultá el instructivo de PIbot.
