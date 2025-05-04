from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.text import Text
import os

# Inicializar Rich Console
console = Console()

load_dotenv()

# Crear cliente de OpenAI
console.print(":gear: [bold blue]Inicializando cliente de OpenAI...[/bold blue]")
client = OpenAI(
    base_url=os.getenv("GITHUB_MODELS_URL"),
    api_key=os.getenv("GITHUB_TOKEN"),
)

# Leer el contenido del archivo Markdown
markdown_file_path = "/workspaces/hoy-empiezo-con-ia-generativa/rag/youtube_guides/configurar_la_audiencia_de_un_canal_o_un_vídeo.md"  # Cambia esto por la ruta de tu archivo Markdown
console.print(f":open_file_folder: [bold green]Leyendo archivo Markdown desde:[/bold green] {markdown_file_path}")
with open(markdown_file_path, "r", encoding="utf-8") as file:
    markdown_content = file.read()

# Pasar el contenido del archivo como input
console.print(":rocket: [bold cyan]Generando embeddings...[/bold cyan]")
response = client.embeddings.create(
    model=os.getenv("GITHUB_MODELS_MODEL_FOR_EMBEDDINGS"),
    input=markdown_content
)

# Imprimir la respuesta
console.print(":sparkles: [bold magenta]Respuesta recibida:[/bold magenta]")
console.print(response)