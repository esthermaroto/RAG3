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


def process_stream_response(stream_response, check_length=False):
    """Process the streaming response from the API"""
    full_response = ""
    for chunk in stream_response:
        if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            yield content
    
    # If we need to check the length, return the full response
    if check_length:
        return full_response


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    model_name = data.get('model')
    description = data.get('description')
    source = data.get('source')
    retry = data.get('retry', False)

    print(f"Source: {source}")
    print(f"Model: {model_name}")
    print(f"Description: {description}")

    def generate_stream():

        print(f"Source for generation: {source}")

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

            # Function to generate title with auto-retry logic
            def generate_title(client, description, is_retry=False):
                system_prompt = ("Eres un experto en generar títulos atractivos para YouTube. "
                                "Genera un único título de máximo 70 caracteres en base a la descripción proporcionada. "
                                "No incluyas comillas ni corchetes. "
                                "Debe ser claro, atractivo y optimizado para SEO."
                                "Devuelve solo el título, sin ningún otro texto adicional. "
                                )
                if is_retry:
                    system_prompt += "Asegúrate absolutamente de que no supere los 70 caracteres."

                # Prepare the parameters for the API call
                params = {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": description},
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
                tokens = encoding.encode(system_prompt + description)
                token_count = len(tokens)

                print(f"🫰🏻 Tokens used: {token_count}")

                return client.chat.completions.create(**params)
            
            # Initial generation
            stream_response = generate_title(client, description, is_retry=retry)
            
            # If auto-retry is needed, we need to collect the full response first
            if not retry:  # Only do auto-retry for initial requests, not manually retried ones
                title = "".join(process_stream_response(stream_response, check_length=True))
                if len(title) > 70:
                    print(f"🚨 Title too long: {len(title)} characters. ✨ Auto-retrying...")
                    # Make a second attempt with retry flag set
                    stream_response = generate_title(client, description, is_retry=True)
                    yield from process_stream_response(stream_response)
                else:
                    # If title is already good, yield it
                    yield title
            else:
                # For manually retried requests, just stream the response
                yield from process_stream_response(stream_response)

        except Exception as e:
            yield f"🤖 Error using OpenAI SDK with {source}: {str(e)}"

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
