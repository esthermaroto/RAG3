from rich import print
from clients.llm_client import create_openai_client, get_model_name
from services.token_counter import count_tokens

def get_title_generation_prompts(description, retry=False, original_title=None):
    """Generate system and user prompts for title generation"""
    system_prompt = ("Eres un experto en generar títulos atractivos para YouTube. "
                    "Genera un único título de máximo 70 caracteres en base a la descripción proporcionada. "
                    "No incluyas comillas, ni simples ni dobles, ni corchetes. "
                    "Debe ser claro, atractivo y optimizado para SEO. "
                    "Devuelve solo el título, sin ningún otro texto adicional. "                            
                    "Usa un tono divertido y atractivo. "
                    "Usa emojis si es posible. "
                    "Si se indica en la descripción que es un capítulo, añade el capitulo al final del título. "
                    "Usando la abreviatura 'Cap.' y el número del capítulo."
                    "Si no se indica que es un capítulo, o que es el vídeo de una serie, no lo incluyas.")
    
    user_prompt = description
    
    # Si es un reintento, modificar los prompts para acortar el título original
    if retry and original_title:
        system_prompt += "Asegúrate ABSOLUTAMENTE de que no supere los 70 caracteres. "
        system_prompt += "Este es un reintento para acortar un título. "
        system_prompt += "Tu respuesta debe tener menos de 70 caracteres. Es CRÍTICO. "
        system_prompt += "IMPORTANTE: Si el título tiene más de 70 caracteres, SERÁ RECHAZADO. "
        
        user_prompt = f"Este título es demasiado largo (tiene {len(original_title)} caracteres): '{original_title}'. "
        user_prompt += f"Por favor acórtalo manteniendo la esencia y las palabras clave importantes. "
        user_prompt += f"Asegúrate absolutamente de que no supere los 70 caracteres."
    
    return system_prompt, user_prompt

def generate_title(source, model_name, description, retry=False, original_title=None):
    """
    Generate a title based on the provided parameters and yield stream response
    
    Args:
        source (str): 'github' or 'ollama'
        model_name (str): Name of the model to use
        description (str): Description to base the title on
        retry (bool): Whether this is a retry attempt
        original_title (str): Original title if this is a retry
    
    Yields:
        str: Chunks of the generated title
    """
    if source not in ['github', 'ollama']:
        yield f"🤔 Unknown source: {source}\n"
        return

    try:
        client = create_openai_client(source)
        if not client:
            yield f"👎🏻 Failed to create client for source: {source}"
            return

        system_prompt, user_prompt = get_title_generation_prompts(
            description, retry, original_title
        )
        
        if retry and original_title:
            print(f"[bold red]REINTENTO SOLICITADO[/bold red]: Acortar título de {len(original_title)} caracteres")
            yield "Acortando título..."

        # Count tokens for logging
        token_count, _ = count_tokens(system_prompt + user_prompt)
        print(f"[bold yellow]Tokens used[/bold yellow]: {token_count}")
        
        # Prepare API parameters
        params = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": True,
            "temperature": 0.9,
            "model": get_model_name(source, model_name)
        }
        
        stream_response = client.chat.completions.create(**params)
        
        full_response = ""
        for chunk in stream_response:
            if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content
        
        # Log the result
        color = "green" if len(full_response) <= 70 else "red"
        print(f"[bold {color}]Longitud final: {len(full_response)} caracteres[/bold {color}]")
        print(f"[bold blue]Título generado: {full_response}[/bold blue]")

    except Exception as e:
        error_message = f"🤖 Error using OpenAI SDK with {source}: {str(e)}"
        print(f"[bold red]ERROR[/bold red]: {error_message}")
        yield error_message