from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from config import GITHUB_MODELS_URL, GITHUB_MODELS_API_KEY, OLLAMA_URL, GITHUB_MODELS_MODEL
from openai import OpenAI


app = Flask(__name__)

CORS(app, resources={r"/*": {"origins":  "http://localhost:5500"}})


def create_openai_client(source):
    """
    Create an OpenAI client based on the source.

    Args:
        source (str): 'github' or 'ollama'

    Returns:
        OpenAI client instance
    """

    print(f"Github Models URL: {GITHUB_MODELS_URL}")
    print(f"Github Models API Key: {GITHUB_MODELS_API_KEY}")

    if source == 'github':
        return OpenAI(
            base_url=GITHUB_MODELS_URL,
            api_key=GITHUB_MODELS_API_KEY
        )
    elif source == 'ollama':
        return OpenAI(
            base_url=f"{OLLAMA_URL}",
            api_key="ollama",  # Ollama doesn't require a real API key, but one is needed for the SDK
        )
    return None


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_messages = data.get('messages', '')
    source = data.get('source', 'github')  # Default to github if not provided

    print(f"User messages: {user_messages}")
    print(f"Source: {source}")

    def generate_stream():     
        client = create_openai_client(source)

        if not client:
            return jsonify({"error": "Failed to create client"}), 500
        
        system_prompt = ("Eres un asistente para la optimización de un canal de Youtube."
                         " Tu tarea es ayudar a los usuarios a mejorar su canal de Youtube"
                         " si te preguntan algo que no sabes, simplemente di que no lo sabes."
                         " si te preguntan algo que no tiene que ver con Youtube, simplemente di que no pudes ayudar con eso.")

        # Asegura que los mensajes estén en el formato correcto
        if isinstance(user_messages, list):
            messages = [{"role": "system", "content": system_prompt}] + user_messages
        else:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": str(user_messages)}
            ]

        # Selección dinámica del modelo
        if source == 'ollama':
            from config import OLLAMA_MODEL
            model = OLLAMA_MODEL
        else:
            model = GITHUB_MODELS_MODEL

        try:
            response = client.chat.completions.create(
                messages=messages,
                stream=True,
                temperature=0.7,
                model=model
            )

            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            import traceback
            print('Error en la llamada a OpenAI client:', e)
            traceback.print_exc()
            yield f"\n[ERROR llamando al modelo: {str(e)}]"

    return Response(generate_stream(), content_type="text/event-stream")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
