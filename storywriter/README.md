# StoryWriter-Implementation

Pasos para poder ejecutar:
<br>1- Crear entorno virtual (si hace falta) y descargar los requirements.txt.

<br>2- Ejecutar "DescargaModeloHF.py" para descargar el modelo de HF.

<br>3- Clonar el repositorio llama.cpp para tener la función que convierte a formato llama con:
<p style="text-align: center;">git clone https://github.com/ggerganov/llama.cpp</p>

<br>5- Ejecutar HFtoGGUF.sh para convertir el modelo de formato HF a GGUS (para usarlo con llama).

<br> Opcional- Usar HF inferencia es para usar modelos pagos en la nube.

<p>
**Diseño de eventos.**
EventSeed
Posee dos tipos de prompts. 
- Generación inicial: crear desde cero una lista preliminar de eventos para la historia.
- Revisión: modificar un evento según las sugerencias del validador.

EventValidator
Tiene un único tipo de prompt. Evalúa cada evento de forma iterativa, considerando también el contexto de los eventos ya aprobados. Indica si el evento debe:
- aceptarse,
- corregirse, o
- regenerarse, proporcionando sugerencias específicas.
<br>
**División en sub-eventos y capítulos.**
SubTasker
Recibe cada evento principal y lo “desmenuza” en sub-eventos más pequeños. Esto permite representar la historia con mayor granularidad. 

ChapterWeaver
Toma todos los sub-eventos y decide: 
- qué sub-eventos van en cada capítulo,
- el orden narrativo adecuado,
- transiciones entre capítulos (incluyendo narrativa no lineal si corresponde).
<br>
**Escritura.**
FinalWriter
Recibe instrucciones y genera el texto narrativo para cada sub-evento. Produce párrafos coherentes con el capítulo y con la historia previa.

Coordinator
Tiene un único tipo de prompt. Evalúa el texto producido por el FinalWriter:
- coherencia con eventos previos,
- estilo narrativo,
- cumplimiento de restricciones,
- fluidez entre capítulos.
Si el texto no cumple los criterios, genera indicaciones de corrección.
</p>