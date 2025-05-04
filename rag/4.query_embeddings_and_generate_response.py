from qdrant_client import QdrantClient
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import os

load_dotenv()
console = Console()

collection_name = os.getenv("QDRANT_COLLECTION_NAME")
client = OpenAI(
    base_url=os.getenv("GITHUB_MODELS_URL"),
    api_key=os.getenv("GITHUB_TOKEN")
)

# Inicializar el cliente de Qdrant
qdrant_client = QdrantClient(url=os.getenv("QDRANT_URL"))

def query_embeddings(query):
    console.print(":mag: [bold cyan]Generando embedding para la consulta...[/bold cyan]")
    embedding_response = client.embeddings.create(
        model=os.getenv("GITHUB_MODELS_MODEL_FOR_EMBEDDINGS"),
        input=query
    )
    query_vector = embedding_response.data[0].embedding

    console.print(":satellite: [bold cyan]Buscando documentos similares en Qdrant...[/bold cyan]")
    search_results = qdrant_client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=3,
        with_payload=True
    ).points

    console.print(f":page_facing_up: [bold green]{len(search_results)} resultados encontrados.[/bold green]")
    return search_results

def generate_response_with_embeddings(query, search_results):
    context = ""
    for i, result in enumerate(search_results):
        title = result.payload.get("titulo", "Sin título")
        part = result.payload.get("parte", 0)
        file_name = result.payload.get("archivo", "Sin archivo")
        context += f"\n--- Información relevante #{i+1} (de {title}, archivo {file_name}, parte {part}) ---\n"
        chunk_text = result.payload.get("text", "No hay texto disponible")
        context += chunk_text + "\n"

    prompt = f"""Responde a la siguiente consulta utilizando la información proporcionada.
                Si la información proporcionada no es suficiente para responder, puedes indicarlo.

                Contexto:
                {context}

                Consulta: {query}

                Respuesta:"""

    system_prompt = ("Eres un asistente experto en creación de contenido para YouTube."
                     "Tu tarea es responder a las preguntas de los usuarios utilizando la información proporcionada en el contexto."
                     "Si la información no es suficiente, indícalo y sugiere buscar más información."
                     "Siempre añade la referencia a la fuente de información utilizada para responder, en fragmento si es posible, y al final de la respuesta, utilizando el formato: "
                     "Referencia: [nombre del archivo] [parte del archivo]")

    console.print(":robot: [bold cyan]Generando respuesta con el modelo...[/bold cyan]")
    response = client.chat.completions.create(
        model=os.getenv("GITHUB_MODELS_MODEL_FOR_GENERATION"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

# 1. Consulta que quiero hacer
query = "¿Qué me aconsejas para subir vídeos a YouTube?"

console.print(Panel(f":thinking_face: [bold yellow]Consulta:[/bold yellow] {query}", title="Consulta del usuario"))

# 2. Obtener los embeddings más similares a la consulta
search_results = query_embeddings(query)

# 3. Generar la respuesta utilizando los embeddings como contexto
result = generate_response_with_embeddings(query, search_results)

# 4. Imprimir la respuesta generada
console.print(Panel(Markdown(result), title=":sparkles: Respuesta Generada", subtitle=":clapper: YouTube Assistant"))
