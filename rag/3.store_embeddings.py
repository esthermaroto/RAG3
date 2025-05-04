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

load_dotenv()

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
    print("Conexión a Qdrant establecida correctamente.")

except Exception as e:
    print(f"Error al conectar a Qdrant: {e}")
    print("No se puede continuar sin una conexión a Qdrant. Asegúrate de que el servidor esté funcionando.")
    sys.exit(1)  # Sale del programa con código de error 1


def recreate_qdrant_collection():
    """
    Elimina y vuelve a crear la colección en Qdrant.
    """

    print(f"Comprobando si la colección {collection_name} ya existe...")    
    
    collections = qdrant_client.get_collections()
    
    # Extraer los nombres de las colecciones
    collection_names = [collection.name for collection in collections.collections]
    
    print(f"Las colecciones disponibles son: {collection_names}")

    if collection_name in collection_names:
        print(f"La colección '{collection_name}' ya existe. Eliminándola...")
        qdrant_client.delete_collection(collection_name)
        print(f"Colección '{collection_name}' eliminada de Qdrant.")
    
    # Crear la colección si no existe
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=3072, distance=Distance.COSINE), # El size debe coincidir con el tamaño de los embeddings. Esto significa que el modelo de OpenAI que estás usando genera vectores de 3072 dimensiones.
      
    )
    print(f"Colección '{collection_name}' creada en Qdrant.")

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

def get_markdown_files(directory):
    """
    Devuelve una lista de archivos Markdown en el directorio especificado.
    """
    return glob.glob(os.path.join(directory, "*.md"))

def process_markdown_files(markdown_files):
    """
   Genera embeddings para cada archivo Markdown y los guarda en Qdrant.
    """    
  
    # Contador para IDs únicos en la base de datos
    id_counter = 0

    # Procesar cada archivo Markdown
    for markdown_file_path in markdown_files:
        # Extraer el nombre del archivo sin la extensión para usarlo como título
        file_name = os.path.basename(markdown_file_path)
        title = os.path.splitext(file_name)[0]
        print(f"\nProcesando archivo: {file_name}")
        
        # Leer el contenido del archivo Markdown
        with open(markdown_file_path, "r", encoding="utf-8") as file:
            markdown_content = file.read()

        # Dividir el contenido en fragmentos más pequeños
        chunks = split_into_chunks(markdown_content, max_tokens=7000)  # Margen de seguridad
        print(f"El archivo {file_name} ha sido dividido en {len(chunks)} fragmentos.")

        # Generar embeddings para cada fragmento
        all_embeddings = []
        for i, chunk in enumerate(chunks):
            print(f"Procesando fragmento {i+1}/{len(chunks)} del archivo {file_name}")
            try:
                response = client.embeddings.create(
                    model=os.getenv("GITHUB_MODELS_MODEL_FOR_EMBEDDINGS"),
                    input=chunk
                )
                all_embeddings.append((response, title, i))
                print(f"Fragmento {i+1} procesado correctamente.")
            except Exception as e:
                print(f"Error al procesar el fragmento {i+1} del archivo {file_name}: {e}")

        # Guardar los embeddings en Qdrant para este archivo
        for i, (embedding_response, file_title, chunk_index) in enumerate(all_embeddings):
            # Extraer el vector de embedding de la respuesta de la API
            vector = embedding_response.data[0].embedding

            # Aquí puedes personalizar cómo se guardan los embeddings
            qdrant_client.upsert(
                collection_name=collection_name,
                points=[{
                    # Usar un entero como ID
                    "id": id_counter,
                    # El vector numérico que representa el contenido del texto
                    "vector": vector,
                    # Metadatos adicionales que quieras almacenar
                    "payload": {
                        "titulo": file_title,
                        "parte": chunk_index,
                        "archivo": file_name,
                        "text": chunks[i]
                    }
                }]
            )
            id_counter += 1
        
        print(f"Embeddings del archivo {file_name} guardados en Qdrant.")
    return id_counter


# Leer todos los archivos Markdown del directorio
markdown_dir_path = "/workspaces/hoy-empiezo-con-ia-generativa/rag/youtube_guides"

markdown_files = get_markdown_files(markdown_dir_path)
print(f"Se encontraron {len(markdown_files)} archivos Markdown para procesar.")

id_counter = process_markdown_files(markdown_files)

print("\nTodos los archivos han sido procesados y guardados en Qdrant.")
print(f"Total de embeddings almacenados: {id_counter}")
