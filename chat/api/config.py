import os
from dotenv import load_dotenv

load_dotenv()

# LLM configuration
GITHUB_MODELS_URL = os.getenv("GITHUB_MODELS_API_URL")
GITHUB_MODELS_MODEL = os.getenv("GITHUB_MODELS_MODEL")
GITHUB_MODELS_API_KEY = os.getenv("GITHUB_MODELS_API_KEY")
OLLAMA_URL = os.getenv("OLLAMA_API_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")