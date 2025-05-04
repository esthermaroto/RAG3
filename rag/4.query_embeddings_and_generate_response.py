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
    search_results = qdrant_client.query_points(
        collection_name=collection_name,
        query=query_vector,
        # Número de resultados a devolver. Si te pasas puede dar error porque te pases del limite de tokens de tu modelo. Prueba cambiando este número.
        limit=3,
        with_payload=True  # Incluir el payload en los resultados
    ).points

    return search_results


def generate_response_with_embeddings(query, search_results):
    # Construir el contexto a partir de los resultados
    context = ""
    for i, result in enumerate(search_results):

        title = result.payload.get("titulo", "Sin título")
        part = result.payload.get("parte", 0)
        file_name = result.payload.get("archivo", "Sin archivo")

        context += f"\n--- Información relevante #{i+1} (de {title}, archivo {file_name}, parte {part}) ---\n"
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

    system_prompt = ("Eres un asistente experto en creación de contenido para YouTube."
                     "Tu tarea es responder a las preguntas de los usuarios utilizando la información proporcionada en el contexto."
                     "Si la información no es suficiente, indícalo y sugiere buscar más información."
                     "Siempre añade la referencia a la fuente de información utilizada para responder, utilizando el formato: "
                     "Referencia: [nombre del archivo] [parte del archivo]")

    # Generar respuesta con el contexto
    response = client.chat.completions.create(
        model=os.getenv("GITHUB_MODELS_MODEL_FOR_GENERATION"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


# 1. Consulta que quiero hacer
# query = "¿Qué me aconsejas para grabar un video?"
# query = "¿Algún consejo para editar vídeos?"
query = "¿Qué me aconsejas para subir vídeos a YouTube?"

# 2. Obtener los embeddings más similares a la consulta
search_results = query_embeddings(query)

# 3. Generar la respuesta utilizando los embeddings como contexto
result = generate_response_with_embeddings(query, search_results)

# 4. Imprimir la respuesta generada
print("\nRespuesta:")
print(result)
