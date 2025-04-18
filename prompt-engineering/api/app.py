from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
import tiktoken

# Load environment variables from a .env file
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


def create_openai_client(source):
    """Create an OpenAI client based on the source"""
    if source == 'github':
        return OpenAI(
            base_url=os.getenv("GITHUB_MODELS_URL"),
            api_key=os.getenv("GITHUB_TOKEN"),
        )
    elif source == 'ollama':
        ollama_url = os.getenv("OLLAMA_URL")
        return OpenAI(
            base_url=f"{ollama_url}/v1",
            api_key="ollama",  # Ollama doesn't require a real API key, but one is needed for the SDK
        )
    return None


def process_stream_response(stream_response):
    """Process the streaming response from the API"""
    for chunk in stream_response:
        if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content


@app.route("/generate")
def generate():
    model_name = request.args.get('model')
    description = request.args.get('description')
    source = request.args.get('source')

    print(f"Source: {source}")
    print(f"Model: {model_name}")
    print(f"Description: {description}")

    def generate_stream():
        if source not in ['github', 'ollama']:
            yield f"Unknown source: {source}\n"
            return

        try:
            client = create_openai_client(source)
            if not client:
                yield f"Failed to create client for source: {source}"
                return

            instructions = (
                "Eres un asistente de IA que ayuda a los usuarios a mejorar sus títulos de vídeos de YouTube. "
                "Aquí tienes los consejos de YouTube:\n\n"
                "## Cómo redactar títulos\n\n"
                "Sé preciso. Asegúrate de que el título represente con exactitud el video. De lo contrario, puede que los usuarios dejen de mirarlo, "
                "lo que puede afectar la visibilidad.\n"
                "Sé breve. Es posible que los usuarios solo vean una parte del título. Por eso, intenta ser breve y colocar las palabras más "
                "importantes cerca del comienzo. Deja los números de episodio y el desarrollo de la marca para el final.\n"
                "Limita el uso de MAYÚSCULAS y emojis. Usa estos recursos con cuidado para enfatizar emociones o elementos especiales en el video. "
                "Por ejemplo, \"Nuestros HIJOS construyeron UN ROBOT 🤖\".\n"
                "Los títulos NO DEBEN execederse entre 40 y 70 caracteres, por lo que debes asegurarte que la suma de caracteres del resultado "
                "no sean más de 70. YouTube solo acepta 100 caracteres. Si el título es demasiado largo, es posible que no se muestre completo "
                "en los resultados de búsqueda o en las vistas previas de los videos.\n\n"
                "### Tipos de títulos de videos\n"
                "Puedes atraer al público con los siguientes recursos:\n\n"
                "- Títulos que se pueden buscar y que describen claramente lo que se puede esperar del video para llegar fácilmente a los usuarios "
                "que buscan contenido similar.\n"
                "- Títulos interesantes que despiertan la curiosidad y atraen a los usuarios que no buscan contenido específico sobre un tema.\n\n"
                "Devuelve solo un título mejorado, incluye emojis, hashtag pero no des explicaciones. No incluyas el nombre del canal ni la fecha de publicación."
            )

            stream_response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": f"{description}"},
                ],
                model=model_name,
                stream=True
            )

            yield from process_stream_response(stream_response)

        except Exception as e:
            yield f"Error using OpenAI SDK with {source}: {str(e)}"

    return Response(generate_stream(), content_type="text/event-stream")


@app.route("/count_tokens", methods=["POST"])
def count_tokens():
    data = request.json

    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data['text']

    try:
        # Get the CL100K base encoding
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        token_count = len(tokens)

        # Create a list to hold the token representations
        token_representations = []
        for token in tokens:
            # Decode each token individually to its text representation
            token_text = encoding.decode([token])
            token_representations.append({
                "token_id": int(token),
                "token_text": token_text
            })

        print(f"Token count: {token_count}")

        return jsonify({
            "token_count": token_count,
            "tokens": token_representations
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
