import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from a .env file
load_dotenv()

# Create OpenAI client
client = OpenAI(
    base_url=os.getenv("GITHUB_MODELS_URL"),
    api_key=os.getenv("GITHUB_TOKEN"),
)


# Call the OpenAI API to generate text
stream_response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Mejorame el siguiente titulo, incluye emojis: '" +
               os.getenv("YOUTUBE_TITLE") + "'"}],
    model="gpt-4o",
    stream=True  # Enable streaming    
)

# Print the response
for chunk in stream_response:
    if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:    
        print(chunk.choices[0].delta.content)
