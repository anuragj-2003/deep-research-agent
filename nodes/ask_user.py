from langgraph.types import interrupt
from states.state import AgentState

def ask_user(state: AgentState):
    """
    Pause for user input using interrupt.
    """
    user_input = interrupt("Please provide the report format (pdf, ppt, md):")
    return {"report_format": user_input}
