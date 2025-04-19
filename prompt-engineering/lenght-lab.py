import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.getenv("GITHUB_MODELS_API_URL"),
    api_key=os.getenv("GITHUB_MODELS_API_KEY"),
    # base_url=os.getenv("OLLAMA_API_URL"),
    # api_key="ollama",

)


def generate_youtube_title(prompt, retry=False):
    """Generate a YouTube title based on the prompt"""

    system_prompt = ("Eres un experto en generar títulos atractivos para YouTube. "
                     "Genera un único título de máximo 70 caracteres en base a la descripción proporcionada. "
                     "No incluyas comillas ni corchetes. "
                     "Debe ser claro, atractivo y optimizado para SEO."
                     "Devuelve solo el título, sin ningún otro texto adicional. "
                     )

    if retry:
        system_prompt += "Asegúrate absolutamente de que no supere los 70 caracteres."

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        # max_tokens=100,
        model=os.getenv("GITHUB_MODELS_MODEL"),
        # model=os.getenv("OLLAMA_MODEL_FOR_TEXT_GENERATION"),
    )

    title = response.choices[0].message.content.strip()

    if len(title) > 70 and not retry:
        print(f"Title too long: {title} with {len(title)} characters. Retrying...")
        return generate_youtube_title(prompt, retry=True)

    return title


if __name__ == "__main__":

    description = "¡Hola developer! 👋🏻 Aquí tienes el segundo vídeo de mi serie sobre IA Generativa para developers. En él nos metemos de lleno en el código, trabajando con uno de los escenarios más comunes: la generación de texto ✍️. Te mostraré cómo llamar a diferentes modelos en modo stream y no-stream, utilizando SDKs como Mistral y OpenAI. Además, veremos una aplicación de ejemplo que te enseñará cómo integrar estos modelos en el frontend, visualizando los resultados que llegan desde una API conectada con GitHub Models🚀 y Ollama 🦙"
    prompt = description
    print(f"Prompt: {prompt}")
    title = generate_youtube_title(prompt)
    print(f"Generated title: {title}")
    print(f"Title length: {len(title)} characters")
