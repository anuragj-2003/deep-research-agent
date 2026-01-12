from states.state import AgentState
from langgraph.types import interrupt

def ask_followup(state: AgentState):
    """
    Interrupt to ask if the user has a follow-up query.
    If yes, updates the topic and continues.
    If no, ends the flow.
    """
    response = interrupt("Would you like to ask a follow-up query? (Enter query or 'no' to finish):")
    
    if response and isinstance(response, str) and response.lower() not in ["no", "n", "none"]:
        # We append the response as a HumanMessage so parse_node can read it
        from langchain_core.messages import HumanMessage
        return {
            "messages": [HumanMessage(content=response)],
            "research_data": [], # Clear data to trigger loop back
            # We DON'T set 'topic' here; let parse_input extract it from the message
            "summary": None,
            "report_content": None
        }
    
    return {} # No state update, will transition to END
