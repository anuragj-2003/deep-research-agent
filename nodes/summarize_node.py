from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from states.state import AgentState
from utils.helpers import load_prompt
import os
import json

def summarize_node(state: AgentState):
    """
    Summarizes the collected research data.
    """
    topic = state.topic
    research_data = state.research_data
    
    # Load prompt
    prompt_template = load_prompt("summary_prompt.txt")
    # In a real tool execution flow, research_data would be populated by the tools output.
    
    # Extract tool outputs from messages to form research data
    tool_outputs = []
    for msg in state.messages:
        if hasattr(msg, 'tool_calls') and len(msg.tool_calls) > 0:
             pass # This is the request
        if hasattr(msg, 'content') and msg.type == 'tool':
             tool_outputs.append(msg.content)
             
    combined_data = "\n\n".join(tool_outputs)
    
    filled_prompt = prompt_template.format(topic=topic, research_data=combined_data)
    
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
    
    response = llm.invoke([HumanMessage(content=filled_prompt)])
    
    return {"summary": response.content}
