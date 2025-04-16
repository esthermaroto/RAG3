import os
from dotenv import load_dotenv
from mistralai import Mistral

# Load environment variables from a .env file
load_dotenv()

# Initialize the Mistral client
client = Mistral(
    api_key=os.getenv("GITHUB_TOKEN"),
    server_url=os.getenv("GITHUB_MODELS_URL")
)

# Call the Mistral API to generate text
stream_response = client.chat.stream(
    model="mistral-small-2503",
    messages=[
        {"role": "user", "content": "Mejorame el siguiente titulo, incluye emojis: '" +
         os.getenv("YOUTUBE_TITLE") + "'"}
    ]   
)

# Print the response
for chunk in stream_response:
    print(chunk.data.choices[0].delta.content)
