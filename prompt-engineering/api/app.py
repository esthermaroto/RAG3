from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
import tiktoken
from rich import print

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5500"}})


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
            content = chunk.choices[0].delta.content
            yield content



@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    model_name = data.get('model')
    description = data.get('description')
    source = data.get('source')
    retry = data.get('retry', False)
    original_title = data.get('originalTitle')

    print(f"Source: {source}")
    print(f"Model: {model_name}")
    print(f"Description: {description}")
    print(f"Retry: {retry}")
    if retry:
        print(f"Original title: {original_title} ({len(original_title) if original_title else 0} chars)")

    def generate_stream():       
        if source not in ['github', 'ollama']:
            yield f"🤔 Unknown source: {source}\n"
            return

        # if source if ollama, we need to remove the prefix
        ollama_model_name = ''
        if source == 'ollama':
            print("Using Ollama")
            ollama_model_name = model_name.split("/")[-1]

            if ollama_model_name == "Phi-4":
                ollama_model_name = "phi4"

            print(f"Model name for Ollama: {ollama_model_name}")

        try:
            client = create_openai_client(source)
            if not client:
                yield f"👎🏻 Failed to create client for source: {source}"
                return

            system_prompt = ("Eres un experto en generar títulos atractivos para YouTube. "
                            "Genera un único título de máximo 70 caracteres en base a la descripción proporcionada. "
                            "No incluyas comillas, ni simples ni dobles, ni corchetes. "
                            "Debe ser claro, atractivo y optimizado para SEO. "
                            "Devuelve solo el título, sin ningún otro texto adicional. "                            
                            "Usa un tono divertido y atractivo. "
                            "Usa emojis si es posible. "
                            "Si se indica en la descripción que es un capítulo, añade el capitulo al final del título. Usando la abreviatura 'Cap.' y el número del capítulo."
                            "Si no se indica que es un capítulo, o que es el vídeo de una serie, no lo incluyas."                            )

            user_prompt = description

            # Si es un reintento, modificar los prompts para acortar el título original
            if retry and original_title:
                system_prompt += "Asegúrate ABSOLUTAMENTE de que no supere los 70 caracteres. "
                system_prompt += "Este es un reintento para acortar un título. "
                system_prompt += "Tu respuesta debe tener menos de 70 caracteres. Es CRÍTICO. "
                # Hacer más énfasis en la longitud máxima
                system_prompt += "IMPORTANTE: Si el título tiene más de 70 caracteres, SERÁ RECHAZADO. "
                
                # Usar el título original como referencia para acortarlo
                user_prompt = f"Este título es demasiado largo (tiene {len(original_title)} caracteres): '{original_title}'. Por favor acórtalo manteniendo la esencia y las palabras clave importantes. Asegúrate absolutamente de que no supere los 70 caracteres."
                print(f"[bold red]REINTENTO SOLICITADO[/bold red]: Acortar título de {len(original_title)} caracteres")
                # Envía un mensaje de inicio para señalar que estamos procesando el reintento
                yield "Acortando título..."

            # Prepare the parameters for the API call
            params = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": True,
                "temperature": 0.8,
            }

            if source == 'ollama':
                params["model"] = ollama_model_name
            else:
                params["model"] = model_name

            # Count how many tokens we are using that include the instructions and the description
            encoding = tiktoken.get_encoding("cl100k_base")
            tokens = encoding.encode(system_prompt + user_prompt)
            token_count = len(tokens)

            print(f"[bold yellow]Tokens used[/bold yellow]: {token_count}")
            
            stream_response = client.chat.completions.create(**params)
            
            full_response = ""
            # Procesar el stream y enviar los chunks al cliente
            for chunk in stream_response:
                if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    # Enviar cada fragmento al cliente
                    yield content
            
            # Verificar longitud al final para debugging
            color = "green" if len(full_response) <= 70 else "red"
            print(f"[bold {color}]Longitud final: {len(full_response)} caracteres[/bold {color}]")
            print(f"[bold blue]Título generado: {full_response}[/bold blue]")

        except Exception as e:
            error_message = f"🤖 Error using OpenAI SDK with {source}: {str(e)}"
            print(f"[bold red]ERROR[/bold red]: {error_message}")
            yield error_message

    return Response(generate_stream(), content_type="text/event-stream")


@app.route("/count_tokens", methods=["POST"])
def count_tokens():
    data = request.json

    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data['text']

    try:
        # Use tiktoken to count tokens        
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
