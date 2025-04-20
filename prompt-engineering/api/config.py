import os
from dotenv import load_dotenv

load_dotenv()

# API configuration
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000
TEMPLATES_AUTO_RELOAD = True
SEND_FILE_MAX_AGE_DEFAULT = 0
CORS_ORIGINS = ["http://localhost:5500"]

# LLM configuration
GITHUB_MODELS_URL = os.getenv("GITHUB_MODELS_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OLLAMA_URL = os.getenv("OLLAMA_URL")

# Encoding for token counting
DEFAULT_ENCODING = "cl100k_base"