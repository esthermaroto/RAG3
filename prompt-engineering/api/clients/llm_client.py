from openai import OpenAI
from config import GITHUB_MODELS_URL, GITHUB_TOKEN, OLLAMA_URL

def create_openai_client(source):
    """Create an OpenAI client based on the source"""
    if source == 'github':
        return OpenAI(
            base_url=GITHUB_MODELS_URL,
            api_key=GITHUB_TOKEN,
        )
    elif source == 'ollama':
        return OpenAI(
            base_url=f"{OLLAMA_URL}/v1",
            api_key="ollama",  # Ollama doesn't require a real API key, but one is needed for the SDK
        )
    return None

def get_model_name(source, model_name):
    """Get the appropriate model name based on the source"""
    if source == 'ollama':
        ollama_model_name = model_name.split("/")[-1]
        
        # Handle special model names
        if ollama_model_name == "Phi-4":
            ollama_model_name = "phi4"
            
        return ollama_model_name
    
    return model_name