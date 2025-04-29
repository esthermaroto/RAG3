from flask import Flask, request, jsonify
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
            base_url=f"{OLLAMA_URL}/v1",
            api_key="ollama",  # Ollama doesn't require a real API key, but one is needed for the SDK
        )
    return None


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    client = create_openai_client('github')

    if not client:
        return jsonify({"error": "Failed to create client"}), 500

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": user_message}
            ],
            stream=True,
            temperature=0.9,
            model=GITHUB_MODELS_MODEL
        )

        full_response = ""
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content

        return jsonify({"response": full_response}), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
