from langgraph.graph import StateGraph, END
from states.state import AgentState, InputState
from nodes.research_node import research_node
from nodes.summarize_node import summarize_node
from nodes.report_node import report_node
from nodes.ask_user import ask_user
from nodes.email_node import ask_email, send_email_node
from nodes.followup_node import ask_followup
from nodes.parse_node import parse_input_node
from langgraph.checkpoint.memory import MemorySaver

def create_graph():
    workflow = StateGraph(AgentState, input=InputState, output=AgentState)
    
    # Add nodes
    workflow.add_node("parse_input", parse_input_node)
    workflow.add_node("research", research_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("ask_user", ask_user)
    workflow.add_node("report", report_node)
    workflow.add_node("ask_email", ask_email)
    workflow.add_node("send_email", send_email_node)
    workflow.add_node("ask_followup", ask_followup)
    
    # Set entry point
    workflow.set_entry_point("parse_input")
    
    # Add edges
    workflow.add_edge("parse_input", "research")
    workflow.add_edge("research", "summarize")
    
    # Conditional edge for HITL
    def check_format(state):
        if state.report_format:
            return "report"
        return "ask_user"
    
    workflow.add_conditional_edges(
        "summarize",
        check_format,
        {"report": "report", "ask_user": "ask_user"}
    )
    
    workflow.add_edge("ask_user", "report")
    workflow.add_edge("report", "ask_email")
    workflow.add_edge("ask_email", "send_email")
    workflow.add_edge("send_email", "ask_followup")
    
    def check_followup(state):
        # Loop logic: If research_data is reset (empty), it means we loop back.
        if state.research_data == []:
             return "research"
        return END

    workflow.add_conditional_edges(
        "ask_followup",
        check_followup,
        {"research": "research", END: END}
    )
    
    # Set up checkpointer
    checkpointer = MemorySaver()
    
    return workflow.compile(checkpointer=checkpointer)
