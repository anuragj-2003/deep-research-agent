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
        # Reset relevant state parts for a fresh run on new topic
        # We keep messages history but might want to add a marker
        return {
            "topic": response,
            "research_data": [], # Clear old data
            "summary": None,
            "report_content": None,
            "report_format": None,
            "email": None
        }
    
    return {} # No state update, will transition to END
