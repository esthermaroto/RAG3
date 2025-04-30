from flask import Blueprint, request, Response
from rich import print
from services.title_generator import generate_title

generate_bp = Blueprint('generate', __name__)

@generate_bp.route("/generate", methods=["POST"])
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
        for text_chunk in generate_title(source, model_name, description, retry, original_title):
            yield text_chunk

    return Response(generate_stream(), content_type="text/event-stream")