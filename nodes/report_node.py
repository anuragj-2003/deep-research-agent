from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from states.state import AgentState
from utils.helpers import load_prompt
from tools.format_tool import create_pdf, create_ppt, create_markdown, create_docx
import os

def report_node(state: AgentState):
    """
    Generates the report in the requested format.
    """
    topic = state.topic
    summary = state.summary
    report_format = state.report_format
    
    # 1. Generate the content using LLM
    
    # Retrieve relevant context from Vector Store
    from utils.vector_store import query_vector_store
    context = query_vector_store(topic, k=3)
    
    # If no context found, fallback to summary
    if not context:
        context = summary or "No research data available."
    
    prompt = load_prompt("report_prompt.txt")
    # We replace 'summary' with 'context' in the prompt logic, or append.
    # Ideally, we should update the prompt template to use 'context' instead of 'summary'.
    # But to minimize prompt changes, let's pass context as summary or modify prompt.
    # The prompt expects {summary}. Let's inject context there.
    filled_prompt = prompt.format(topic=topic, summary=context, report_format=report_format)
    
    from utils.config import LLM_MODEL, GROQ_API_KEY
    llm = ChatGroq(model=LLM_MODEL, api_key=GROQ_API_KEY)
    response = llm.invoke([HumanMessage(content=filled_prompt)])
    content = response.content
    
    # 2. Save to file
    filename = f"{topic.replace(' ', '_')}_report.{report_format}"
    # Ensure reports dir exists
    if not os.path.exists("reports"):
        os.makedirs("reports")
    
    filepath = os.path.join("reports", filename)
    
    if report_format == "pdf":
        create_pdf(content, filepath)
    elif report_format == "ppt":
        create_ppt(content, filepath)
    elif report_format == "docx":
        create_docx(content, filepath)
    else:
        create_markdown(content, filepath)
        
    return {"report_content": content, "messages": [HumanMessage(content=f"Report generated: {filepath}")]}
