from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from states.state import AgentState
from utils.helpers import load_prompt, clear_reports_dir
from tools.search_tool import tavily_search
from tools.scraper_tool import scrape_website
import os
import json

def research_node(state: AgentState):
    """
    Orchestrates the research process.
    """
    # Clear reports at the start of research (assumes new thread/start or new loop)
    # We check if research_data is empty (which happens on start AND on loop reset)
    if not state.research_data: 
         clear_reports_dir()

    topic = state.topic
    research_data = state.research_data
    
    # Load prompt
    prompt_template = load_prompt("research_prompt.txt")
    filled_prompt = prompt_template.format(topic=topic, research_data=json.dumps(research_data, indent=2))
    
    # Initialize LLM
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
    llm_with_tools = llm.bind_tools([tavily_search, scrape_website])
    
    messages = [SystemMessage(content=filled_prompt)] + state.messages
    
    # Basic ReAct Loop
    # Loop until the LLM stops calling tools or we hit a limit
    
    current_messages = messages
    
    for _ in range(3):
        try:
             response = llm_with_tools.invoke(current_messages)
        except Exception as e:
             return {"messages": [HumanMessage(content=f"Error in research LLM call: {e}")]}

        current_messages.append(response)
        
        if not response.tool_calls:
            # Done researching
            break
            
        # Execute tools
        for tool_call in response.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            call_id = tool_call['id']
            
            tool_output = "Error: Tool not found"
            if tool_name == "tavily_search_results_json":
                tool_output = tavily_search.invoke(tool_args)
            elif tool_name == "scrape_website":
                tool_output = scrape_website.invoke(tool_args)
            
            from langchain_core.messages import ToolMessage
            # Convert tool output to string for message
            tool_msg = ToolMessage(content=str(tool_output), tool_call_id=call_id, name=tool_name)
            current_messages.append(tool_msg)
            
            # Index the TOOL OUTPUT into Vector Store (This is the raw research data)
            from utils.vector_store import add_to_vector_store
            # Helper to convert list/dict output to string
            content_to_index = str(tool_output)
            add_to_vector_store([content_to_index], metadatas=[{"source": tool_name, "topic": topic}])

    # Return ALL new messages (including tool calls and outputs) so state is updated
    # calculate new messages by slicing from original length
    new_messages = current_messages[len(messages):]
    return {"messages": new_messages}
