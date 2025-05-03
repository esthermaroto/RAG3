from openai import OpenAI
from dotenv import load_dotenv
import os
import tiktoken
import re

load_dotenv()

client = OpenAI(
    base_url=os.getenv("GITHUB_MODELS_URL"),
    api_key=os.getenv("GITHUB_TOKEN"),
)

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

# Leer el contenido del archivo Markdown
markdown_file_path = "/workspaces/hoy-empiezo-con-ia-generativa/rag/youtube_guides/configurar_la_audiencia_de_un_canal_o_un_vídeo.md"  # Cambia esto por la ruta de tu archivo Markdown
with open(markdown_file_path, "r", encoding="utf-8") as file:
    markdown_content = file.read()

# Dividir el contenido en fragmentos más pequeños
chunks = split_into_chunks(markdown_content, max_tokens=7000)  # Margen de seguridad
print(f"El contenido ha sido dividido en {len(chunks)} fragmentos.")

# Generar embeddings para cada fragmento
all_embeddings = []
for i, chunk in enumerate(chunks):
    print(f"Procesando fragmento {i+1}/{len(chunks)}")
    try:
        response = client.embeddings.create(
            model=os.getenv("GITHUB_MODELS_MODEL"),
            input=chunk
        )
        all_embeddings.append(response)
        print(f"Fragmento {i+1} procesado correctamente.")
    except Exception as e:
        print(f"Error al procesar el fragmento {i+1}: {e}")

# Imprimir la respuesta
for i, embedding in enumerate(all_embeddings):
    print(f"Embedding del fragmento {i+1}:")
    print(embedding)