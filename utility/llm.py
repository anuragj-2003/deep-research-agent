import os
from langchain_groq import ChatGroq


def get_llm(temperature: float = 0.2):
    """
    Returns a configured LLM using Groq API.
    A junior-level approach using try-except to catch missing keys or errors.
    """
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY is not set in environment variables.")
        
        # We can default to the user's requested model
        model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        llm = ChatGroq(
            api_key=api_key,
            model_name=model_name,
            temperature=temperature,
            max_retries=5
        )
        return llm
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        # Return none or raise depending on how we handle failure upstream
        raise e
