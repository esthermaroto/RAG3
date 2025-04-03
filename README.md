# Hoy empiezo con IA Generativa

¡Hola developer! Este repo contiene todo lo que necesitas para empezar a trabajar con IA generativa. Desde qué puedes usar para empezar gratis en tu máquina local, o en la nube, hasta ejemplos de los diferentes conceptos que necesitas aprender para poder usar IA generativa en tus proyectos. La idea de este repo es llevarlo a una serie de casos prácticos que te ayuden a entender cómo funciona la IA generativa pero también que sirva para algo útil 🤓. En mi caso lo voy a basar en diferentes necesidades que tengo a la hora de publicar un nuevo vídeo. Pero... empecemos por el principio.

## ¿Qué es IA generativa?

La IA generativa es un tipo de inteligencia artificial que puede crear contenido nuevo y original, como texto, imágenes, música y más. Utiliza algoritmos avanzados y modelos de aprendizaje profundo para generar resultados creativos y únicos.

## ¿Qué puedes hacer con IA generativa?

- ✏️ Generar texto: Puedes crear artículos, historias, poemas y más utilizando modelos de lenguaje como GPT-3.
- 🌅 Crear imágenes: Puedes generar imágenes y arte utilizando modelos como DALL-E o Midjourney.
- 🎶 Componer música: Puedes crear melodías y composiciones musicales utilizando IA generativa.
- 📋 Automatizar tareas: Puedes utilizar IA generativa para automatizar tareas repetitivas y mejorar la eficiencia en el trabajo.
- 🤖 Crear chatbots: Puedes desarrollar chatbots inteligentes que interactúan con los usuarios de manera natural.
- 👩🏼‍💻 Generar código: Puedes utilizar IA generativa para escribir y depurar código, lo que puede acelerar el proceso de desarrollo.
- 💡 Mejorar la creatividad: Puedes utilizar IA generativa como una herramienta para inspirarte y mejorar tu creatividad en diferentes campos.

Y estos son solo algunos ejemplos. Pero lo importante aquí es que entiendas que la IA Generativa tiene como principal objetivo crear.

Vale, ¿y cómo empiezo con todo esto? La IA Generativa utiliza lo que se conocen modelos que están entrenados, mejor o peor, para saber crear todo esto. Hay de diferentes tipos, tamaños y proveedores. Así que vamos a empezar por ver cómo puedo montarme un entorno donde pueda probar estos modelos para en posteriores vídeos elegir unos u otros dependiendo de lo que necesite.

## ¿Qué necesitas para empezar?

Lo primero que necesitas es un entorno de desarrollo y lo más importante de todo es que necesitas "algo" que pueda ejecutar los modelos de IA Generativa. Aquí 👇🏻 te dejo algunas opciones:

- Ollama: Ollama es una herramienta de código abierto que te permite ejecutar modelos de IA generativa en tu máquina local. Puedes instalarla fácilmente y empezar a usarla con solo unos pocos comandos. [Ollama](https://ollama.com/)
- Docker Model Runner: Relativamente nuevo y no está soportado todavía en todos los sistemas operativos o arquitecturas pero si eres un desarrollador que trabaja con contenedores, puede ser una opción interesante para explorar. [Docker Model Runner](https://www.docker.com/)
- GitHub Models: esta última opción, también gratuita, te permite poder acceder a una variedad de modelos de IA generativa que puedes utilizar directamente en tus proyectos en fase de desarrollo y no necesitas instalar nada adicional. [GitHub Models](https://github.com/)

# Ollama

Puedes instalarlo localmente, por ejemplo en tu Mac a través de Homebrew:

```bash
brew install ollama
```

O descargandote los ejecutables directamente desde su [página de descargas](https://ollama.com/download).

También puedes ejecutarlo dentro de un Dev Container, lo cual te evita tener que instalarlo directamente en tu máquina local. Sin embargo, debes tener en cuenta de que para la mayoría de modelos que es humanamente posible ejecutarlos en una máquina local, vas a necesitar reservar unos 16gb, como poco, de memoria RAM para que pueda ejecutar los modelos. Si quieres probarlo, este repositorio tiene todo lo que necesitas para tenerlo funcionando si abres el mismo dentro de un contenedor.

Si estás en local, una vez que ya lo tengas instalado, necesitas primeramente arrancar ollama:

```bash
ollama serve
```

Si estás dentro de un dev container, no es necesario que lo hagas, ya que el contenedor ya lo tiene arrancado.

Con esto tienes arrancada la herramienta que va a permitirte ejecutar los modelos de IA generativa en tu máquina local. Pero por ahora no tienes ningún modelo descargado que poder ejecutar. Para ello, muy al estilo Docker, puedes descargar modelos usando `ollama pull` y ejecutarlos con `ollama run`. Ok, pero qué modelos puedo descargar? Puedes ver una lista de los modelos disponibles ejecutando el siguiente comando:



```bash
ollama list
```


y descargar alguno de los modelos, por ejemplo el de Mistral (no te preocupes, ya veremos más adelante qué modelos son los que vas a ir necesitando)

```bash
ollama pull mistral-nemo
```

Para ver cuántos modelos tienes descargados, puedes ejecutar el siguiente comando:

```bash
ollama list
```

Ok, ¿y ahora qué hago con esto? Puedes ejecutar este modelo en concreto:

```bash
ollama run mistral-nemo "Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"
```

O incluso lo puedes ejecutar para que puedas llamarlo de forma programática, a través de un API REST:

```bash
ollama run mistral-nemo
```

Para saber qué modelos tienes ejecutandose, puedes lanzar el siguiente comando:

```bash
ollama ps
```

Y a partir de este momento también puedes hacer peticiones a través de un cliente HTTP, como Postman o Insomnia, o incluso desde tu propio código. 

```bash
curl http://localhost:11434/api/generate \
-d '{ "model": "mistral-nemo", "stream": false, "prompt":"Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"}' \
| jq .response
```

La lista de modelos disponibles para Ollama la puedes encontrar aquí: https://ollama.com/library

Si quieres probar otros la forma es la misma:

```bash
ollama run gemma3 "Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"
```

O incluso Deepseek-r1 que está ahora muy de moda:

```bash
ollama run deepseek-r1 "Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"
```

Al igual que en Docker, no hace falta hacer primeramente un `pull` del modelo, sino que puedes ejecutarlo directamente y si no tienes el modelo en local se encargará de descargarlo.

Y también puedes eliminar cualquiera de los modelos descargados usando el mismo estilo:

```bash
ollama rm mistral
```

## Docker Model Runner

Hace apenas unos días, Docker anunció [Docker Model Runner](https://docs.docker.com/desktop/features/model-runner/). Esta otra opción está todavía en fase beta y no está soportada en todos los sistemas operativos o arquitecturas. Pero lo único que debes hacer en este caso, si tienes instalado Docker Desktop es tenerlo actualizado, al menos a la versión 4.40 o superior.


El "problema" de estos dos primeros es que necesitas hardware suficiente para poder ejecutar los modelos en tu local y que esto no sea un sufrimiento. Por ejemplo, en el repo de GitHub de ollama se indica lo siguiente:

> [Note]
>You should have at least 8 GB of RAM available to run the 7B models, 16 GB to run the 13B models, and 32 GB to run the 33B models.

Y como te puedes imaginar, no todo el mundo tiene maquinones para poder ejecutar esto.

## GitHub Models

La tercera opción que puedes utilizar, si las anteriores no son posibles para ti es Github Models. El cual es un marketplace de modelos de IA que puedes utilizar en fase de desarrollo de forma gratuita. Para poder utilizarlo solo necesitas tener una cuenta de GitHub y generar un Personal Access Token que nisiquiera necesita tener ningún scope.

## AI Toolkit for Visual Studio

Y ya para terminar, si vas a utilizar Visual Studio Code como parte de tu entorno de desarrollo tienes una extensión disponible muy interesante que se llama AI Toolkit for Visual Studio, la cual te va a permitir interactuar de una forma bastante sencilla con los modelos tanto de Ollama como de Github Models (además de otras opciones que no hemos visto aquí). Esta extensión forma parte de este DevContainer.

Puedo cargar directamente los modelos que ya he descargado de Ollama y ejecutarlos utilizando el Playground que ofrece.
