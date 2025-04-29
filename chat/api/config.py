import os
from dotenv import load_dotenv

load_dotenv()

# LLM configuration
GITHUB_MODELS_URL = os.getenv("GITHUB_MODELS_API_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OLLAMA_URL = os.getenv("OLLAMA_URL")
GITHUB_MODELS_MODEL = os.getenv("GITHUB_MODELS_MODEL")
GITHUB_MODELS_API_KEY = os.getenv("GITHUB_MODELS_API_KEY")