import os
from typing import Optional

def load_prompt(prompt_name: str) -> str:
    """
    Loads a prompt from the prompts/ directory.
    Args:
        prompt_name: The name of the file (e.g., 'research_prompt.txt')
    Returns:
        The content of the prompt file.
    """
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_path = os.path.join(base_path, "prompts", prompt_name)
    
    try:
        with open(prompt_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Prompt file {prompt_name} not found at {prompt_path}")
        return ""

from utils.vector_store import clear_vector_store

def clear_reports_dir():
    """
    Clears all files in the reports/ directory and resets the vector store.
    """
    # 1. Clear text reports
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reports_path = os.path.join(base_path, "reports")
    
    if os.path.exists(reports_path):
        for filename in os.listdir(reports_path):
            file_path = os.path.join(reports_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

    # 2. Clear vector store
    clear_vector_store()
