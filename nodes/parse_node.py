from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from states.state import AgentState
from utils.helpers import load_prompt
import os
import json
from typing import Optional
from pydantic import BaseModel, Field

class ParsedInput(BaseModel):
    topic: str = Field(description="The main research topic")
    report_format: Optional[str] = Field(description="The requested report format (pdf, ppt, docx, md)", default=None)
    email: Optional[str] = Field(description="The user's email address if provided", default=None)

def parse_input_node(state: AgentState):
    """
    Parses the user's initial input to extract topic, format, and email.
    """
    # Get the latest user message
    # In the initial state, it should be the last human message or the very first one.
    # We look for the most recent generic input.
    user_input = ""
    for msg in reversed(state.messages):
        if isinstance(msg, HumanMessage) or (hasattr(msg, 'type') and msg.type == 'human'):
             user_input = msg.content
             break
    
    if not user_input:
        return {}

    system_prompt = """
    You are an intelligent intent parser for a research agent.
    Extract the following information from the user's request:
    1. Research Topic (The main subject to research)
    2. Report Format (pdf, ppt, docx, or md). Normalize to these codes.
    3. Email Address (If provided).

    Return JSON matching this schema:
    {
        "topic": "string",
        "report_format": "string or null",
        "email": "string or null"
    }
    
    Example:
    Input: "Research quantum computing and send a pdf to bob@example.com"
    Output: { "topic": "Quantum Computing", "report_format": "pdf", "email": "bob@example.com" }
    """
    
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"), temperature=0)
    structured_llm = llm.with_structured_output(ParsedInput)
    
    try:
        result = structured_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ])
        
        updates = {"topic": result.topic}
        if result.report_format:
            # Normalize format just in case
            fmt = result.report_format.lower()
            if "pdf" in fmt: fmt = "pdf"
            elif "ppt" in fmt: fmt = "ppt" 
            elif "doc" in fmt: fmt = "docx"
            elif "md" in fmt or "mark" in fmt: fmt = "md"
            updates["report_format"] = fmt
            
        if result.email:
            updates["email"] = result.email
            
        return updates
        
    except Exception as e:
        print(f"Error parsing input: {e}")
        # Fallback: Just assume the whole input is the topic if parsing fails
        return {"topic": user_input}
