import os
from dotenv import load_dotenv
from openai import OpenAI
import time

# Load environment variables from a .env file
load_dotenv()

# Create OpenAI client
client = OpenAI(
    base_url=os.getenv("GITHUB_MODELS_URL"),
    api_key=os.getenv("GITHUB_TOKEN"),
)


start_time = time.time()

# Call the OpenAI API to generate text
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Mejorame el siguiente titulo, incluye emojis: '" +
               os.getenv("YOUTUBE_TITLE") + "'"}],
    model="gpt-4o"
)

end_time = time.time()
execution_time = end_time - start_time

# Print the response
print(response.choices[0].message.content)
print(f"Execution time: {execution_time} seconds")
