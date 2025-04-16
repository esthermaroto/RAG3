# Generación de texto con IA Generativa

¡Hola developer 👋🏻! En esta sección vas a poder aprender cómo trabajar con modelos de IA Generativa para pedirles que te ayuden a generar texto en base a uno que tú le pases. Además vamos aprovechar este capítulo para introducir algunos conceptos que son útiles cuando comienzas en este mundo. El vídeo relacionado con este contenido puedes encontrarlo en mi canal de YouTube:

[![creando textos con IA Generativa](https://github.com/user-attachments/assets/308be690-a399-490a-a9c9-74f47652abcc)](https://youtu.be/-FZtKYuDsgQ)

¡No te olvides de suscribirte a mi canal 🥲!

## Introducción

La generación de texto con IA es un campo de la inteligencia artificial que se centra en la creación de modelos que puedan generar texto de forma autónoma. Estos modelos se entrenan en grandes cantidades de texto y luego se les pide que generen texto en función de una entrada dada. La generación de texto con IA se utiliza en una amplia variedad de aplicaciones, como la generación de contenido para sitios web, la creación de diálogos para chatbots y la redacción de informes y artículos. Para mi ejemplo voy a tener como objetivo *mejorar títulos de vídeos para mi canal de YouTube*, de tal forma que puedas entender estos conceptos con un ejemplo práctico.

## Qué modelos utilizar

Lo primero que necesitas averiguar es qué modelos de IA puedes utilizar para esta tarea. La forma más sencilla de averiguarlo es buscar en marketplaces como puede ser el de Ollama o en GitHub Models, o incluso usando la extensión que te mostré en el vídeo anterior llamada [AI Toolkit for Visual Studio Code](https://learn.microsoft.com/es-es/windows/ai/toolkit/). En Github Models puedes encontrar de forma sencilla modelos buscando por `Capability`y eligiendo `Chat/completion` y verás que tenemos diferentes modelos que podemos usar. ¿Cuál elegir? Bueno, eso depende de tus necesidades y de tus recursos. Algunos modelos son más grandes y más potentes que otros, pero también requieren más recursos para ejecutarse. Si estás empezando, te recomiendo que pruebes con un modelo pequeño y luego vayas subiendo en complejidad a medida que te sientas más cómod@. Por ejemplo para este vídeo voy a elegir cuatro modelos que están disponibles en GitHub Models:

- `Mistral NeMo`: es un modelo desarrollado por una star-up francesa, Mistral AI, en colaboración con NVIDIA. Está disponible bajo licencia Apache 2.0 (gratuito). La ventana de contexto es de 128.000 tokens, no es multimodal y soporta múltiples idiomas.

- `GPT-4o`: es un modelo desarrollado por Open AI, una empresa de inteligencia artificial basada en San Francisco. Es un modelo de pago. Tiene una ventana de contexto de 128.000 tokens, es multimodal y soporta múltiples idiomas.

- `Deepseek-R1`: es un modelo de lenguaje de última generación desarrollado por DeepSeek AI, es un modelo gratuito pero tiene un versión alojada en la nube. Tiene una ventana de contexto de 128.000 tokens, no es multimodal y se puede liar un poco si no le pides las cosas en inglés o chino.

- `Phi-4`:  es un modelo desarrollado por Microsoft y es de pago. Tiene una ventana de contexto de 16.000 tokens, no es multimodal y soporta múltiples idiomas.

Por otro lado, vamos a ver también otros modelos, además de estos, usando Ollama:

- `Gemma 3`: Es un modelo desarrollado por Google, es un modelo abierto, tiene una ventana de 128.000 tokens, puedes procesar tanto texto como imágenes y soporta múltiples idiomas.

- `Llama 3.1`: Es un modelo desarrollado por Meta (Facebook), gratuito, soporta también hasta 128.000 tokens y soporta múltiples idiomas. No es multimodal.

## Ya tengo el modelo ¿ahora qué? APIs y SDKs

Una vez que hayas elegido un modelo, necesitas averiguar cómo vas a interactuar con él. Afortunadamente, hay muchas opciones disponibles, desde APIs hasta SDKs. Lo habitual es que trabajes con un SDK en lugar de llamar a la API REST directamente para que sea más sencillo. Algunos modelos vienen con su propio SDK, como el de Mistral, pero si no es el caso, puedes utilizar un SDK genérico como Hugging Face o OpenAI. Durante el vídeo verás que utilizo tanto el de Mistral como el de OpenAI como puedes ver en el directorio `no_streaming` y `with_streaming`

## Stream o no stream... That's the question!

Cuando estés trabajando con un modelo de IA generativa, es importante tener en cuenta si vas a trabajar en modo stream o no. Algunos modelos están diseñados para trabajar en modo stream, lo que significa que puedes enviarles una entrada y obtener una salida en tiempo real. Otros modelos no están diseñados para trabajar en modo stream, lo que significa que tienes que enviarles toda la entrada de una vez y luego esperar a que te devuelvan toda la salida. Los ejemplos del directorio `no_streaming` te muestran cómo es la experiencia del usuario cuando tienes que esperar que cuando lo vas recibiendo poco a poco. Por el contrario, en el directorio `with_streaming` podrás ver cómo te devuelve el contenido de a pocos, según lo vaya generando el modelo de IA. Es habitual que en las interfaces de usuario se utilice el modo stream, mientras que en las aplicaciones de backend se utilice el modo no stream.

## Aplicación de ejemplo

Para finalizar con esta sección, he creado una aplicación web que consta de dos partes:

- `web`: una aplicación muy simple, con solo HTML y JavaScript, sin frameworks ni nada, que representa una web en la que integro mi nueva funcionalidad de generación de títulos para los vídeos de mi canal de YouTube y que hace uso de una API para llamar a los modelos.
- `api`: API REST creada con Python y Flask, la cual recibe peticiones de la web y, dependendiendo de los parámetros recibidos llama a un modelo que está en GitHub Models o en Ollama.

Con este ejemplo puedes ver de forma sencilla cómo lo aprendido puede ser integrado en una aplicación que tú desarrolles, más allá de los chat o playgrounds que te encuentres por ahí 😃

¡Nos vemos 👋🏻!
