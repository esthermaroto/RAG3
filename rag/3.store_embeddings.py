from calendar import c
import sys
from httpx import get
from openai import OpenAI
from dotenv import load_dotenv
import os
import tiktoken
import re
import glob
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from rich.console import Console
from rich.progress import track

load_dotenv()
console = Console()

collection_name = os.getenv("QDRANT_COLLECTION_NAME")

client = OpenAI(
    base_url=os.getenv("GITHUB_MODELS_URL"),
    api_key=os.getenv("GITHUB_TOKEN"),
)

# Inicializar el cliente de Qdrant
qdrant_client = QdrantClient(url=os.getenv("QDRANT_URL"))

# Comprobar la conexión a Qdrant
try:
    qdrant_client.get_collections()
    console.print(":rocket: [bold green]Conexión a Qdrant establecida correctamente.[/bold green]")
except Exception as e:
    console.print(f":x: [bold red]Error al conectar a Qdrant:[/bold red] {e}")
    console.print(":warning: [yellow]No se puede continuar sin una conexión a Qdrant. Asegúrate de que el servidor esté funcionando.[/yellow]")
    sys.exit(1)  # Sale del programa con código de error 1

def recreate_qdrant_collection():
    """
    Elimina y vuelve a crear la colección en Qdrant.
    """
    console.print(f":mag: [cyan]Comprobando si la colección [bold]{collection_name}[/bold] ya existe...[/cyan]")    
    
    collections = qdrant_client.get_collections()
    collection_names = [collection.name for collection in collections.collections]
    console.print(f":file_folder: [blue]Las colecciones disponibles son:[/blue] {collection_names}")

    if collection_name in collection_names:
        console.print(f":wastebasket: [yellow]La colección '[bold]{collection_name}[/bold]' ya existe. Eliminándola...[/yellow]")
        qdrant_client.delete_collection(collection_name)
        console.print(f":white_check_mark: [green]Colección '[bold]{collection_name}[/bold]' eliminada de Qdrant.[/green]")
    
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
    )
    console.print(f":sparkles: [bold green]Colección '[bold]{collection_name}[/bold]' creada en Qdrant.[/bold green]")

def split_into_chunks(text, max_tokens=8000, encoding_name="cl100k_base"):
    encoding = tiktoken.get_encoding(encoding_name)
    paragraphs = re.split(r'\n\n+', text)
    chunks = []
    current_chunk = []
    current_token_count = 0

    for paragraph in paragraphs:
        paragraph_tokens = len(encoding.encode(paragraph))
        if paragraph_tokens > max_tokens:
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            for sentence in sentences:
                sentence_tokens = len(encoding.encode(sentence))
                if current_token_count + sentence_tokens <= max_tokens:
                    current_chunk.append(sentence)
                    current_token_count += sentence_tokens
                else:
                    if current_chunk:
                        chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [sentence]
                    current_token_count = sentence_tokens
        else:
            if current_token_count + paragraph_tokens > max_tokens:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [paragraph]
                current_token_count = paragraph_tokens
            else:
                current_chunk.append(paragraph)
                current_token_count += paragraph_tokens

    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks

def get_markdown_files(directory):
    return glob.glob(os.path.join(directory, "*.md"))

def process_markdown_files(markdown_files):
    # Primero cuenta el número total de fragmentos
    total_chunks = 0
    file_chunks = []
    
    for markdown_file_path in markdown_files:
        file_name = os.path.basename(markdown_file_path)
        title = os.path.splitext(file_name)[0]
        
        with open(markdown_file_path, "r", encoding="utf-8") as file:
            markdown_content = file.read()

        chunks = split_into_chunks(markdown_content, max_tokens=7000)
        total_chunks += len(chunks)
        file_chunks.append((markdown_file_path, file_name, title, chunks))
    
    console.print(f":scissors: [yellow]Total de fragmentos a procesar: [bold]{total_chunks}[/bold][/yellow]")
    
    # Ahora procesa todos los fragmentos con una única barra de progreso
    id_counter = 0
    with console.status("[bold green]Procesando fragmentos...") as status:
        for markdown_file_path, file_name, title, chunks in file_chunks:
            console.print(f"\n:page_facing_up: [bold blue]Procesando archivo:[/bold blue] {file_name}")
            console.print(f":scissors: [yellow]El archivo tiene [bold]{len(chunks)}[/bold] fragmentos.[/yellow]")
            
            all_embeddings = []
            for i, chunk in enumerate(chunks):
                status.update(f"[bold green]Procesando fragmento {i+1}/{len(chunks)} de {file_name}[/bold green]")
                try:
                    response = client.embeddings.create(
                        model=os.getenv("GITHUB_MODELS_MODEL_FOR_EMBEDDINGS"),
                        input=chunk
                    )
                    all_embeddings.append((response, title, i))
                except Exception as e:
                    console.print(f":x: [red]Error al procesar el fragmento {i+1} del archivo {file_name}: {e}[/red]")
            
            for i, (embedding_response, file_title, chunk_index) in enumerate(all_embeddings):
                vector = embedding_response.data[0].embedding
                qdrant_client.upsert(
                    collection_name=collection_name,
                    points=[{
                        "id": id_counter,
                        "vector": vector,
                        "payload": {
                            "titulo": file_title,
                            "parte": chunk_index,
                            "archivo": file_name,
                            "text": chunks[i]
                        }
                    }]
                )
                id_counter += 1
            
            console.print(f":floppy_disk: [bold green]Embeddings del archivo {file_name} guardados en Qdrant.[/bold green]")
    return id_counter

console.print(":sparkles: [bold green]Iniciando el proceso de creación de embeddings...[/bold green]")

console.print(":wastebasket: [yellow]Eliminando la colección anterior de Qdrant (si existe)...[/yellow]")
recreate_qdrant_collection()

markdown_dir_path = "/workspaces/hoy-empiezo-con-ia-generativa/rag/youtube_guides"
markdown_files = get_markdown_files(markdown_dir_path)
console.print(f":mag: [cyan]Se encontraron [bold]{len(markdown_files)}[/bold] archivos Markdown para procesar.[/cyan]")

id_counter = process_markdown_files(markdown_files)

console.print("\n:star2: [bold green]Todos los archivos han sido procesados y guardados en Qdrant.[/bold green]")
console.print(f":chart_with_upwards_trend: [bold blue]Total de embeddings almacenados: {id_counter}[/bold blue]")
