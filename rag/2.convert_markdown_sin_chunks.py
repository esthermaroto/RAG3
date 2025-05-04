from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url=os.getenv("GITHUB_MODELS_URL"),
    api_key=os.getenv("GITHUB_TOKEN"),
)

# Leer el contenido del archivo Markdown
markdown_file_path = "youtube_guides/configurar_la_audiencia_de_un_canal_o_un_vídeo.md"  # Cambia esto por la ruta de tu archivo Markdown
with open(markdown_file_path, "r", encoding="utf-8") as file:
    markdown_content = file.read()

# Pasar el contenido del archivo como input
response = client.embeddings.create(
    model=os.getenv("GITHUB_MODELS_MODEL_FOR_EMBEDDINGS"),
    input=markdown_content
)

# Imprimir la respuesta
print(response)