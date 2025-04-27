# Prompt Engineering

¡Hola developer 👋🏻! Este contenido forma parte del vídeo Prompt Engineering de mi serie sobre IA Generativa. En esta sección he dejado unas cuantas demos para que puedas entender qué reglas debes conocer relacionadas con el Prompt Engineering.

## ¿Qué es el Prompt Engineering?

El Prompt Engineering es el arte de formular preguntas o instrucciones a un modelo de IA para obtener respuestas más precisas y útiles. Es una habilidad esencial para cualquier persona que trabaje con IA Generativa, ya que la calidad de las respuestas que obtienes depende en gran medida de cómo formules tus preguntas. Pero en este vídeo no quería hablarte de la teoría, sino de la práctica. Así que he preparado una serie de demos para que puedas ver cómo funciona el Prompt Engineering en acción.

En el vídeo anterior sobre generación de texto, usé como ejemplo el siguiente prompt:

```markdown
Mejorame el siguiente titulo, incluye emojis: {title}
```

Sin embargo, cada uno de los modelos que utilicé durante el vídeo me daban respuestas muy diferentes. Esto es así porque cada uno de los modelos tiene su propia forma de interpretar el prompt. Pero hay una serie de reglas que puedes seguir para mejorar la calidad de las respuestas que obtienes. Así que durante el vídeo, te mostré cómo cambié mi prompt para obtener mejores resultados.

Para mostrarte de forma sencilla y ágil qué resultados dan estas reglas voy a utilizar una herramienta llamada Prompty, que me permite hacer pruebas rápidas con diferentes modelos de IA. Puedes encontrarla en [prompty.dev](https://prompty.dev/). En esta herramienta, puedes elegir entre varios modelos de IA y probar diferentes prompts para ver cómo responden.


## ¿Cuáles son las reglas del Prompt Engineering?

El Prompt Engineering es una habilidad que se puede aprender y mejorar con la práctica. Hay varias reglas que puedes seguir para mejorar la calidad de las respuestas que obtienes de un modelo de IA. Estas reglas son aplicables a cualquier modelo de IA, independientemente de su arquitectura o diseño. Aunque no son reglas estrictas, seguirlas te ayudará a obtener mejores resultados en tus interacciones con modelos de IA.

### Regla #1: Sé específico

Cuanto más específico seas en tu prompt, mejor será la respuesta que obtendrás. Siguiendo con el mismo ejemplo, si le dices a un modelo de IA que te ayude a mejorar un título, pero no le das ningún contexto, es probable que obtengas una respuesta genérica. En cambio, si le das más información sobre el tema o el público al que va dirigido, es más probable que obtengas una respuesta más relevante.
Por ejemplo, en lugar de decir "Mejora este título", podrías decir "Mejora este título para un artículo sobre IA Generativa dirigido a desarrolladores". Esto le dará al modelo más contexto y aumentará la probabilidad de que obtengas una respuesta útil. En mi caso, cambié el pasarle el título por pasarle la descripción del vídeo, por lo que el modelo tenía más contexto sobre lo que estaba buscando. 


### Regla #2: Usa ejemplos

Si tienes ejemplos de lo que estás buscando, inclúyelos en tu prompt. Esto le dará al modelo una mejor idea de lo que quieres y aumentará la probabilidad de que obtengas una respuesta relevante.
Por ejemplo, en lugar de decir "Mejora este título", podrías decir "Mejora este título: 'Hoy empiezo con IA Generativa' a algo como '¡Hoy es el día! Comenzando mi viaje en IA Generativa 🚀'". Esto le dará al modelo una mejor idea de lo que estás buscando y aumentará la probabilidad de que obtengas una respuesta útil.

### Regla #3: Usa un tono claro y conciso
Evita usar jerga o lenguaje técnico que pueda confundir al modelo. En su lugar, usa un tono claro y conciso que sea fácil de entender. Esto aumentará la probabilidad de que obtengas una respuesta relevante.
Por ejemplo, en lugar de decir "Mejora este título usando un lenguaje técnico", podrías decir "Mejora este título usando un lenguaje claro y sencillo". Esto le dará al modelo una mejor idea de lo que estás buscando y aumentará la probabilidad de que obtengas una respuesta útil.

Hay muchas más reglas que puedes seguir para mejorar la calidad de las respuestas que obtienes de un modelo de IA, pero estas son algunas de las más importantes. Recuerda que el Prompt Engineering es una habilidad que se puede aprender y mejorar con la práctica. Así que no dudes en experimentar y probar diferentes enfoques para ver qué funciona mejor para ti.

## Evaluar la respuesta

Por otro lado, también mostré durante el vídeo que es importante evaluar la respuesta que obtienes del modelo. No todas las respuestas son útiles o relevantes, así que asegúrate de evaluar la calidad de la respuesta que obtienes y ajusta tu prompt en consecuencia. Esto te ayudará a obtener mejores resultados en tus interacciones con modelos de IA. En este vídeo te introduje al concepto llamado LLM as a Judge, que es una forma de evaluar la calidad de las respuestas que obtienes de un modelo de IA. Este concepto se basa en la idea de que un modelo de IA puede ser visto como un juez que evalúa la calidad de una respuesta en función de ciertos criterios. Estos criterios pueden incluir la relevancia, la claridad y la utilidad de la respuesta. Te dejé un montón de ejemplos en el directorio `llm-as-a-judge` para que puedas ver cómo funciona este concepto en la práctica.

Además, es fundamental recordar que la retroalimentación constante y la iteración en tus prompts son clave para mejorar la calidad de las respuestas que obtienes.




Referencias:
- [Prompt Engineering](https://www.promptengineering.org/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

