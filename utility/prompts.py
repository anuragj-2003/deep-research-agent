import os

def load_prompt(filename: str) -> str:
    """
    Loads text content from the prompts/ directory.
    Basic try-except block for junior-level readability.
    """
    try:
        # Resolve path relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_path = os.path.join(project_root, "prompts", filename)
        
        with open(prompt_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error loading prompt '{filename}': {e}")
        return ""
