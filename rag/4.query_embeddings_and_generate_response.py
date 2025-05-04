from qdrant_client import QdrantClient
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

collection_name = "youtube_guides"
client = OpenAI(
    base_url=os.getenv("GITHUB_MODELS_URL"),
    api_key=os.getenv("GITHUB_TOKEN")
)

# Inicializar el cliente de Qdrant
qdrant_client = QdrantClient(url=os.getenv("QDRANT_URL"))

# Definir una función para realizar consultas
def query_embeddings(query):
    # 1. Convertir la consulta a un embedding
    embedding_response = client.embeddings.create(
        model=os.getenv("GITHUB_MODELS_MODEL_FOR_EMBEDDINGS"),
        input=query
    )
    query_vector = embedding_response.data[0].embedding
    
    # 2. Buscar documentos similares en Qdrant
    search_results = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=3,  # Número de resultados a devolver
        with_payload=True  # Incluir el payload en los resultados
    )
    
    return search_results

def generate_response_with_embeddings(query, search_results):
    # Construir el contexto a partir de los resultados
    context = ""
    for i, result in enumerate(search_results):
        title = result.payload.get("titulo", "Sin título")
        part = result.payload.get("parte", 0)
        
        context += f"\n--- Información relevante #{i+1} (de {title}, parte {part}) ---\n"
        # Agregamos el texto completo recuperado del documento
        chunk_text = result.payload.get("text", "No hay texto disponible")
        context += chunk_text + "\n"
    
    # Crear el prompt final combinando la consulta con el contexto
    prompt = f"""Responde a la siguiente consulta utilizando la información proporcionada.
Si la información proporcionada no es suficiente para responder, puedes indicarlo.

Contexto:
{context}

Consulta: {query}

Respuesta:"""

    # Generar respuesta con el contexto
    response = client.chat.completions.create(
        model=os.getenv("GITHUB_MODELS_MODEL_FOR_GENERATION"),
        messages=[
            {"role": "system", "content": "Eres un asistente experto en creación de contenido para YouTube."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

# 1. Consulta que quiero hacer
query = "¿Qué me aconsejas para grabar un video?"

# 2. Obtener los embeddings más similares a la consulta
search_results = query_embeddings(query)

# 3. Generar la respuesta utilizando los embeddings como contexto
result = generate_response_with_embeddings(query, search_results)

# 4. Imprimir la respuesta generada
print("\nRespuesta:")
print(result)





