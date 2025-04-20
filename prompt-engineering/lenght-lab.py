import os
from openai import OpenAI
from dotenv import load_dotenv
from rich import print

load_dotenv()

client = OpenAI(
    base_url=os.getenv("GITHUB_MODELS_API_URL"),
    api_key=os.getenv("GITHUB_MODELS_API_KEY"),
    # base_url=os.getenv("OLLAMA_API_URL"),
    # api_key="ollama",

)


def generate_youtube_title(prompt, retry=False, original_title=None):
    """Generate a YouTube title based on the prompt"""

    system_prompt = ("Eres un experto en generar títulos atractivos para YouTube. "
                     "Genera un único título de máximo 70 caracteres en base a la descripción proporcionada. "
                     "No incluyas comillas ni corchetes. "
                     "Debe ser claro, atractivo y optimizado para SEO."
                     "Devuelve solo el título, sin ningún otro texto adicional. "
                     )

    if retry:
        system_prompt += "Asegúrate absolutamente de que no supere los 70 caracteres."
        # Usar el título original como referencia para acortarlo
        prompt = f"Este título es demasiado largo (tiene {len(original_title)} caracteres): '{original_title}'. Por favor acórtalo manteniendo la esencia y las palabras clave importantes, pero que tenga máximo 70 caracteres."

    # Print the system and user prompts for debugging
    print(
        f"[bold blue]System prompt[/bold blue]: [blue]{system_prompt}[/blue]")
    print(f"[bold yellow]User prompt[/bold yellow]: [yellow]{prompt}[/yellow]")

    print(f"[bold pink]Model for title generation 📝[/bold pink]: {os.getenv('GITHUB_MODELS_MODEL_FOR_TEXT_GENERATION')}")

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=1,
        # max_tokens=100,
        model=os.getenv("GITHUB_MODELS_MODEL_FOR_TEXT_GENERATION"),
        # model=os.getenv("OLLAMA_MODEL_FOR_TEXT_GENERATION"),
    )

    title = response.choices[0].message.content.strip()

    if len(title) > 70 and not retry:
        print(
            f"🚨 Title too long: '{title}' with {len(title)} characters. Retrying with original title...")
        
        return generate_youtube_title(prompt, retry=True, original_title=title)

    return title


if __name__ == "__main__":

    description = (
        "¡Hola developer! 👋🏻 Aquí tienes el segundo vídeo de mi serie sobre IA Generativa para developers. "
        "En él nos metemos de lleno en el código, trabajando con uno de los escenarios más comunes: la generación de texto ✍️. "
        "Te mostraré cómo llamar a diferentes modelos en modo stream y no-stream, utilizando SDKs como Mistral y OpenAI. "
        "Además, veremos una aplicación de ejemplo que te enseñará cómo integrar estos modelos en el frontend, visualizando los "
        "resultados que llegan desde una API conectada con GitHub Models🚀 y Ollama 🦙"
    )
    prompt = description

    title = generate_youtube_title(prompt)

    print(f"[bold green]✨Generated title[/bold green]: '{title}'")
    print(f"[bold yellow]Title length: {len(title)} characters[/bold yellow]")
