import os
import prompty
# import invoker
import prompty.openai
from dotenv import load_dotenv

load_dotenv()

# execute the prompt
response = prompty.execute("/workspaces/hoy-empiezo-con-ia-generativa/prompt-engineering/llm-as-a-judge/clarity.prompty",
                           configuration={
                               "name": os.getenv('GITHUB_MODELS_MODEL'),
                               "type": "openai",
                               "base_url": os.getenv('GITHUB_MODELS_API_URL'),
                               "api_key": os.getenv('GITHUB_MODELS_API_KEY')
                           })

print(response)