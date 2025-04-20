from flask import Blueprint, request, jsonify
from rich import print
from services.token_counter import count_tokens

tokens_bp = Blueprint('tokens', __name__)

@tokens_bp.route("/count_tokens", methods=["POST"])
def count_tokens_route():
    data = request.json

    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data['text']

    try:
        token_count, token_representations = count_tokens(text)
        print(f"Token count: {token_count}")

        return jsonify({
            "token_count": token_count,
            "tokens": token_representations
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500