import os
import sys
from pathlib import Path
from tabulate import tabulate
import json
import prompty
from dotenv import load_dotenv
import prompty.openai


load_dotenv()


def run_evaluator(evaluator_path):
    """
    Run a prompty evaluator and return the score and explanation.
    """
    try:

        # Run the evaluator using prompty as a library
        evaluator_file = str(evaluator_path)
        result = prompty.execute(evaluator_file)

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
                lines = result_str.strip().split('\n')
                for line in lines:
                    if line.lower().startswith('score:'):
                        try:
                            score = line.split(':', 1)[1].strip()
                            break
                        except IndexError:
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

    # Check if we have environments loaded
    print("Environment variables loaded:")
    print(f"OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL')}")
    print(f"OLLAMA_API_URL: {os.getenv('OLLAMA_API_URL')}")
    print(f"OLLAMA_API_KEY: {os.getenv('OLLAMA_API_KEY')}")

    # Find the evaluators directory
    evaluators_dir = Path.cwd() / 'prompt-engineering/evaluators'

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

    # Run each evaluator and collect results
    results = []
    for evaluator_file in evaluator_files:
        print(f"Running evaluator: {evaluator_file.name}")
        result = run_evaluator(evaluator_file)
        results.append(result)

    # Display results in a table
    headers = ['Evaluator', 'Score', 'Explanation']
    table_data = [[result['evaluator'], result['score'],
                   result['explanation']] for result in results]

    print("\nEvaluation Results:")
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


if __name__ == "__main__":
    main()
