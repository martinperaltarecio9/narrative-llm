# Narrative - LLM

**Autores**: Martín Peralta y Lautaro De Gyldenfeldt.

El objetivo inicial del trabajo fue realizar un sistema de seis agentes capaz de escribir historias narrativas coherentes e interesantes. La idea surgió de la incapacidad de los LLMs generativos de mantener el hilo de los hechos cuando se le pide escribir historias medianamente largas. 

Al terminar el sistema decidimos que una buena forma de complementarlo era explorando el tema de "Author Imitation", intentando obtener un LLM que escriba como un determinado autor de nuestra elección. Fue así como diseñamos un experimento que involucró realizar fine-tune con el uso de adapters (LoRa) de un modelo de lenguaje más el entrenamiento de un discriminador de texto del autor que buscábamos imitar. Obtuvimos resultados interesantes que se muestran más adelante en este archivo.

A continuación dejamos una explicación de ambos ejes del trabajo, un análisis de resultados y nuestras conclusiones.

## "StoryWriter" - Sistema de Agentes

El sistema consta de 3 etapas y 2 agentes por cada una. Las etapas son generación de eventos, división en capítulos y sub-eventos, y escritura final. Todo el sistema es orquestado desde un único archivo 'controller.py'. Desde aquí se realizan los llamados al modelo con un formato de prompt fijo para cada acción de cada agente en el orden y con la lógica que se explica.

**Generación de eventos**

EventSeed. 
Posee dos tipos de prompts.
- Generación: crear, tomando como punta de partida los eventos ya aprobados (o no), el evento que le sigue.
- Revisión: modificar un evento según las sugerencias del validador.

EventValidator. 
Tiene un único tipo de prompt. Evalúa cada evento de forma iterativa, considerando también el contexto de los eventos ya aprobados. Indica si el evento debe:
- aceptarse,
- corregirse, o
- regenerarse, proporcionando sugerencias específicas.

**División en sub-eventos y capítulos**

SubTasker.
Recibe cada evento principal y lo “desmenuza” en sub-eventos más pequeños. Esto permite representar la historia con mayor granularidad. 

ChapterWeaver.
Toma todos los sub-eventos y decide: 
- qué sub-eventos van en cada capítulo,
- el orden narrativo adecuado,
- transiciones entre capítulos (incluyendo narrativa no lineal si corresponde).

**Escritura**

FinalWriter.
Recibe instrucciones y genera el texto narrativo para cada sub-evento. Produce párrafos coherentes con el capítulo y con la historia previa.

Coordinator.
Tiene un único tipo de prompt. Evalúa el texto producido por el FinalWriter:
- coherencia con eventos previos,
- estilo narrativo,
- cumplimiento de restricciones,
- fluidez entre capítulos.
Si el texto no cumple los criterios, genera indicaciones de corrección.

**Ejemplo de uso**

**Falta insertar un png con un ejemplo**

## Imitación de autores (Shakespeare)

El experimento constó de 4 etapas:
- obtención del dataset tanto para el fine-tune del modelo como para el discriminador y la validación final, 
- fine-tune de un LLM sobre las obras de un autor de nuestra elección,
- entrenamiento de un discriminador basado en RoBERTa que determine si un texto fue o no escrito por el autor en cuestión,
- y una comparación del modelo fine-tuned + el modelo base + ChatGPT con prompt engineering usando el discriminador (más una medición de la perplexity).

**Dataset**

Necesitábamos un autor que cumpliera con: 
- fácil acceso a sus obras,
- una forma de escribir peculiar,
- y una gran cantidad de texto escrito. 
Es por esto que inmediatamente pensamos en Shakespeare, que cumple las tres condiciones. 
Además, pensando en la elaboración del discriminador, obtuvimos texto de autores con un estilo lingüístico parecido al de Shakespeare: Christopher Marlowe y Benjamin Jonson. La idea era que podíamos usar los textos de estos autores para hacer que el discriminador realmente aprenda a distinguir a Shakespeare: si le pasáramos como clase negativa texto de Wikipedia no serviría de nada.
Es así como obtuvimos, en formato .txt, texto sacado de Wikipedia + las obras de Shakespeare, Marlowe y Jonson.

**Fine-Tune**

Utilizamos Mistral 7B (instruction-tuned) en formato local compatible con Hugging Face para realizar inferencia y generación de texto mediante prompts. Hicimos fine-tune con LoRa 