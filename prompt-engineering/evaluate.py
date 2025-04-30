import os
import sys
from pathlib import Path
import json
import os
import sys
from pathlib import Path
import json
import time
from dotenv import load_dotenv
import prompty.openai
from rich import print
from rich.table import Table

load_dotenv()


def run_evaluator(evaluator_path, new_title, description, use_ollama=True):
    """
    Run a prompty evaluator and return the score and explanation.
    """
    try:
        # Select configuration based on provider
        if use_ollama:
            configuration = {
                "name": os.getenv('OLLAMA_MODEL'),
                "type": "openai",
                "base_url": os.getenv('OLLAMA_API_URL'),
                "api_key": os.getenv('OLLAMA_API_KEY')
            }
        else:
            configuration = {
                "name": os.getenv('GITHUB_MODELS_MODEL'),
                "type": "openai",
                "base_url": os.getenv('GITHUB_MODELS_API_URL'),
                "api_key": os.getenv('GITHUB_MODELS_API_KEY')
            }

        # Run the evaluator
        result = prompty.execute(
            str(evaluator_path),
            inputs={"generated_title": new_title, "video_description": description},
            configuration=configuration
        )

        # Process the result
        if isinstance(result, dict):
            score = result.get('score', 'N/A')
            explanation = result.get('explanation', 'No explanation provided.')
        else:
            result_str = str(result)
            score = 'N/A'
            explanation = result_str

            # Try to parse JSON from string result
            if isinstance(result, str):
                try:
                    parsed_result = json.loads(result)
                    score = parsed_result.get('score', 'N/A')
                    explanation = parsed_result.get('explanation', result_str)
                except json.JSONDecodeError:
                    pass

        return {
            'evaluator': evaluator_path.name,
            'score': score,
            'explanation': explanation
        }
    except Exception as e:
        return {
            'evaluator': evaluator_path.name,
            'score': 'Error',
            'explanation': str(e)
        }


def generate_title(description, use_ollama=True):
    """Generate a title based on the description using the appropriate model."""
    if use_ollama:
        model_name = os.getenv('OLLAMA_MODEL_FOR_TEXT_GENERATION')
        base_url = os.getenv('OLLAMA_API_URL')
        api_key = os.getenv('OLLAMA_API_KEY')
    else:
        model_name = os.getenv('GITHUB_MODELS_MODEL_FOR_TEXT_GENERATION')
        base_url = os.getenv('GITHUB_MODELS_API_URL')
        api_key = os.getenv('GITHUB_MODELS_API_KEY')
    
    print(f"[bold blue]Model for title generation 📝[/bold blue]: {model_name}")
    
    start_time = time.time()
    
    title = prompty.execute(
        Path.cwd() / "prompt-engineering/generate_title.prompty",
        inputs={"description": description},
        configuration={
            "name": model_name,
            "type": "openai",
            "base_url": base_url,
            "api_key": api_key
        }
    )
    
    elapsed_time = time.time() - start_time
    
    print(f"Generated title ✨: {title}")
    print(f"Title generation executed in {elapsed_time / 60:.2f} minutes 🕒.")
    
    return title


def run_evaluations(title, description, use_ollama=True):
    """Run all evaluators and display results."""
    provider_name = "Ollama 🦙" if use_ollama else "Github Models 🚀"
    model_name = os.getenv('OLLAMA_MODEL') if use_ollama else os.getenv('GITHUB_MODELS_MODEL')
    
    print(f"Evaluator using [bold green]{model_name}[/bold green]")
    
    # Find the evaluators directory
    evaluators_dir = Path.cwd() / 'prompt-engineering/llm-as-a-judge'
    
    if not evaluators_dir.exists() or not evaluators_dir.is_dir():
        print(f"Error: '{evaluators_dir}' directory not found.")
        return
    
    # Find all evaluator files
    evaluator_files = [f for f in evaluators_dir.iterdir()
                       if f.is_file() and f.suffix == '.prompty']
    
    if not evaluator_files:
        print(f"Error: No evaluator files found in '{evaluators_dir}'.")
        return
    
    print(f"Found {len(evaluator_files)} evaluators in '{evaluators_dir}'.")
    
    # Run evaluators and collect results
    results = []
    total_elapsed_time = 0
    
    for evaluator_path in evaluator_files:
        print(f"Running evaluator: {evaluator_path.name}")
        start_time = time.time()
        
        result = run_evaluator(evaluator_path, title, description, use_ollama=use_ollama)
        
        elapsed_time = time.time() - start_time
        total_elapsed_time += elapsed_time
        
        print(f"Evaluator '{evaluator_path.name}' executed in {elapsed_time / 60:.2f} minutes 🕒")
        results.append(result)
    
    # Display results in a table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Evaluator", style="dim")
    table.add_column("Score")
    table.add_column("Explanation")
    
    for result in results:
        score = int(result['score']) if str(result['score']).isdigit() else 0
        score_color = "green" if score == 5 else "yellow" if score in [3, 4] else "red"
        
        table.add_row(
            result['evaluator'],
            f"[bold {score_color}]{result['score']}[/bold {score_color}]",
            str(result['explanation'])
        )
    
    print(table)
    print(f"\nTotal time for all evaluations: {total_elapsed_time / 60:.2f} minutes 🕒")


def main(use_ollama=True):
    """Main function to run the entire evaluation process."""
    description = "¡Hola developer! 👋🏻 Aquí tienes el segundo vídeo de mi serie sobre IA Generativa para developers. En él nos metemos de lleno en el código, trabajando con uno de los escenarios más comunes: la generación de texto ✍️. Te mostraré cómo llamar a diferentes modelos en modo stream y no-stream, utilizando SDKs como Mistral y OpenAI. Además, veremos una aplicación de ejemplo que te enseñará cómo integrar estos modelos en el frontend, visualizando los resultados que llegan desde una API conectada con GitHub Models y Ollama 🚀."
    
    # Run with Ollama
    print("Starting with Ollama 🦙")
    title_ollama = generate_title(description, use_ollama=True)
    run_evaluations(title_ollama, description, use_ollama=True)
    
    # Run with GitHub Models
    print("Now let's run the same with Github Models 🚀")
    title_github = generate_title(description, use_ollama=False)
    run_evaluations(title_github, description, use_ollama=False)
    
    print("Evaluation process completed. Thank you for using the evaluator! 🚀")


if __name__ == "__main__":
    main()
