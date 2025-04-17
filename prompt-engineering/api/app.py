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
        ollama_url = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
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
    title = request.args.get('title')    
    source = request.args.get('source')

    print(f"Source: {source}")
    print(f"Model: {model_name}")
    print(f"Title: {title}")

    def generate_stream():
        if source not in ['github', 'ollama']:
            yield f"Unknown source: {source}\n"
            return

        try:
            client = create_openai_client(source)
            if not client:
                yield f"Failed to create client for source: {source}"
                return
                
            stream_response = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": f"Mejorame el siguiente titulo, incluye emojis: '{title}'"}
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
