import prompty
# import invoker
import prompty.openai
from dotenv import load_dotenv

load_dotenv()

# execute the prompt
response = prompty.execute("/workspaces/hoy-empiezo-con-ia-generativa/prompt-engineering/llm-as-a-judge/clarity.prompty")

print(response)