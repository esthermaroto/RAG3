import os
import sys
from pathlib import Path
from tabulate import tabulate
import json
from dotenv import load_dotenv
import prompty.openai
import time
from rich import print
from rich.table import Table

load_dotenv()


def run_evaluator(evaluator_path, new_title, description):
    """
    Run a prompty evaluator and return the score and explanation.
    """
    try:
        # Run the evaluator using prompty as a library
        evaluator_file = str(evaluator_path)

        result = prompty.execute(evaluator_file,
                                 inputs={
                                     "generated_title": new_title, "video_description": description
                                 })

        # Process the result based on type
        if isinstance(result, dict):
            score = result.get('score', 'N/A')
            explanation = result.get('explanation', 'No explanation provided.')
        else:
            # If not a dictionary, convert to string
            result_str = str(result)
            score = 'N/A'
            explanation = result_str

            # Try to find score in the output if it's a string
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


def main():

    description = "¡Hola developer! 👋🏻 Aquí tienes el segundo vídeo de mi serie sobre IA Generativa para developers. En él nos metemos de lleno en el código, trabajando con uno de los escenarios más comunes: la generación de texto ✍️. Te mostraré cómo llamar a diferentes modelos en modo stream y no-stream, utilizando SDKs como Mistral y OpenAI. Además, veremos una aplicación de ejemplo que te enseñará cómo integrar estos modelos en el frontend, visualizando los resultados que llegan desde una API conectada con GitHub Models y Ollama 🚀."

    start_time = time.time()

    print(
        f"[bold blue]Model for title generation 📝[/bold blue]: {os.getenv('OLLAMA_MODEL_FOR_TEXT_GENERATION')}")

    # Get the new title
    new_title = prompty.execute(
        Path.cwd() / "prompt-engineering/ollama.prompty",
        inputs={"description": description}
    )

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Generated title ✨: {new_title}")
    print(f"Title generation executed in {elapsed_time / 60:.2f} minutes 🕒.")

    print(f"Evaluator using [bold green]{os.getenv('OLLAMA_MODEL')}[/bold green]")

    # Find the evaluators directory
    evaluators_dir = Path.cwd() / 'prompt-engineering/llm-as-a-judge'

    if not evaluators_dir.exists() or not evaluators_dir.is_dir():
        print(f"Error: '{evaluators_dir}' directory not found.")
        sys.exit(1)

    # Find all evaluator files in the directory
    evaluator_files = [f for f in evaluators_dir.iterdir(
    ) if f.is_file() and f.suffix == '.prompty']

    if not evaluator_files:
        print(f"Error: No evaluator files found in '{evaluators_dir}'.")
        sys.exit(1)

    print(f"Found {len(evaluator_files)} evaluators in '{evaluators_dir}'.")

    # Track total elapsed time for all evaluators
    total_elapsed_time = 0

    # Run each evaluator and collect results
    results = []
    for evaluator_file in evaluator_files:
        print(f"Running evaluator: {evaluator_file.name}")
        start_time = time.time()
        result = run_evaluator(evaluator_file, new_title, description)
        end_time = time.time()

        elapsed_time = end_time - start_time
        total_elapsed_time += elapsed_time

        print(
            f"Evaluator '{evaluator_file.name}' executed in {elapsed_time / 60:.2f} minutes 🕒")
        results.append(result)


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


    # Display total elapsed time
    print(
        f"\nTotal time for all evaluations: {total_elapsed_time / 60:.2f} minutes 🕒")


if __name__ == "__main__":
    main()
