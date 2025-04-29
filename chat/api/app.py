from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins":  "http://localhost:5500"}})


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    # Aquí deberías conectar con tu modelo de IA real
    ai_response = f"Respuesta simulada a: {user_message}"
    return jsonify({'response': ai_response})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
