from openai import OpenAI
from dotenv import load_dotenv
import os
import tiktoken
import re
from rich.console import Console
from rich.progress import track

# Inicializar Rich Console
console = Console()

load_dotenv()

markdown_file_path = "/workspaces/hoy-empiezo-con-ia-generativa/rag/youtube_guides/configurar_la_audiencia_de_un_canal_o_un_vídeo.md"

client = OpenAI(
    base_url=os.getenv("GITHUB_MODELS_URL"),
    api_key=os.getenv("GITHUB_TOKEN"),
)


def read_markdown_file(file_path):
    """
    Lee el contenido de un archivo Markdown y lo devuelve como una cadena.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content


def split_into_chunks(text, max_tokens=8000, encoding_name="cl100k_base"):
    """
    Divide el texto en fragmentos más pequeños que no superen el límite de tokens.
    """
    # Inicializar el codificador
    encoding = tiktoken.get_encoding(encoding_name)

    # Dividir el texto en párrafos (o por alguna otra unidad lógica)
    paragraphs = re.split(r'\n\n+', text)

    chunks = []
    current_chunk = []
    current_token_count = 0

    for paragraph in paragraphs:
        # Contar tokens del párrafo actual
        paragraph_tokens = len(encoding.encode(paragraph))

        # Si un párrafo individual excede el límite, dividirlo en frases
        if paragraph_tokens > max_tokens:
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            for sentence in sentences:
                sentence_tokens = len(encoding.encode(sentence))
                if current_token_count + sentence_tokens <= max_tokens:
                    current_chunk.append(sentence)
                    current_token_count += sentence_tokens
                else:
                    # Guardar el chunk actual y comenzar uno nuevo
                    if current_chunk:  # Evitar guardar chunks vacíos
                        chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [sentence]
                    current_token_count = sentence_tokens
        else:
            # Si agregar este párrafo excede el límite, guardar el chunk actual y comenzar uno nuevo
            if current_token_count + paragraph_tokens > max_tokens:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [paragraph]
                current_token_count = paragraph_tokens
            else:
                current_chunk.append(paragraph)
                current_token_count += paragraph_tokens

    # No olvidar guardar el último chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks


def generate_embeddings(chunks):
    all_embeddings = []
    for i, chunk in track(enumerate(chunks), description="Generando embeddings... 🚀", total=len(chunks)):
        try:
            response = client.embeddings.create(
                model=os.getenv("GITHUB_MODELS_MODEL_FOR_EMBEDDINGS"),
                input=chunk
            )
            all_embeddings.append(response)
            console.log(f"[green]Fragmento {i+1} procesado correctamente. ✅[/green]")
        except Exception as e:
            console.log(f"[red]Error al procesar el fragmento {i+1}: {e} ❌[/red]")
    
    return all_embeddings


def print_embeddings(all_embeddings):
    # Imprimir la respuesta
    for i, embedding in enumerate(all_embeddings):
        console.print(f"[bold blue]Embedding del fragmento {i+1}:[/bold blue] 📊")
        console.print(embedding)


# 1. Leer el contenido del archivo Markdown
console.print("[cyan]Leyendo el archivo Markdown... 📄[/cyan]")
markdown_content = read_markdown_file(markdown_file_path)

# 2. Dividir el contenido en fragmentos más pequeños
console.print("[cyan]Dividiendo el contenido en fragmentos... ✂️[/cyan]")
chunks = split_into_chunks(markdown_content, max_tokens=7000)  # Margen de seguridad
console.print(f"[green]El archivo ha sido dividido en {len(chunks)} fragmentos. ✅[/green]")

# 3. Generar embeddings para cada fragmento
all_embeddings = generate_embeddings(chunks)

# Pulsa una tecla para mostrar los embeddings
console.print("[yellow]Pulsa Enter para mostrar los embeddings generados...[/yellow]")
input()

# 4. Imprimir la respuesta
console.print("[cyan]Imprimiendo los embeddings generados... 📊[/cyan]")
print_embeddings(all_embeddings)