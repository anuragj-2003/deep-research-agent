from typing import Dict, Any
from dotenv import load_dotenv

# Load env variables first
load_dotenv()

from langgraph.graph import StateGraph, END
from langgraph.types import RetryPolicy

from state.state import ResearchState, InputState
from nodes.planner import node_plan, node_subqueries, continue_to_search
from nodes.searcher import search_worker, search_join, can_advance_after_search
from nodes.reader import plan_reads, read_worker, read_join, can_advance_after_read, continue_to_read
from nodes.synthesizer import node_synthesize, node_reflect, should_continue

def build_graph():
    """
    Builds the workflow graph using our Nodes.
    """
    graph = StateGraph(state_schema=ResearchState, input_schema=InputState)
    
    # Standard retry policy: 3 attempts with exponential backoff
    api_retry = RetryPolicy(initial_interval=1.5, backoff_factor=2.0, max_attempts=3)
    
    # Add Nodes with dynamic retry routing
    graph.add_node("generate_plan", node_plan, retry=api_retry)
    graph.add_node("generate_subqueries", node_subqueries, retry=api_retry)
    
    graph.add_node("execute_search", search_worker, retry=api_retry)
    graph.add_node("wait_for_searches", search_join)
    
    graph.add_node("select_sources_to_read", plan_reads)
    graph.add_node("read_selected_sources", read_worker, retry=api_retry)
    graph.add_node("wait_for_reads", read_join)
    
    graph.add_node("synthesize_draft", node_synthesize, retry=api_retry)
    graph.add_node("evaluate_draft", node_reflect, retry=api_retry)
    
    # Define output node that just acts as an explicit final destination
    def output_results(state: ResearchState) -> ResearchState:
        return state

    def download_the_report(state: ResearchState) -> ResearchState:
        from langgraph.types import interrupt
        import os
        
        # Human-in-the-loop: Ask the user for the delivery email
        receiver_email = interrupt("Please provide the receiver email address for the generated report:")
        
        if not receiver_email or not isinstance(receiver_email, str) or "@" not in receiver_email:
            print("[main] Invalid or missing email address provided via interrupt. Skipping email delivery.")
            return state
            
        print(f"[main] Downloading report and emailing to {receiver_email}")
        
        # We need to import it here to avoid circular imports if any, or at top
        from utility.email_sender import send_research_report
        report: str = state.get("answer_draft", "")
        topic: str = state.get("question", "Research Report")
        
        # Append citations if any exist
        citations = state.get("citations", [])
        if citations and "References" not in report:
            refs = "\n".join([f"[{i+1}] {u}" for i, u in enumerate(citations)])
            report += "\n\n## References\n" + refs
            
        # Generate Document
        from utility.doc_generator import generate_docx
        docx_stream = generate_docx(topic, report)
        
        send_research_report(receiver_email, topic, report, attachment_bytes=docx_stream)
        return state

    graph.add_node("output_results", output_results)
    graph.add_node("download_the_report", download_the_report)
    
    # Graph Flow
    graph.set_entry_point("generate_plan")
    graph.add_edge("generate_plan", "generate_subqueries")
    
    # Search Phase
    graph.add_conditional_edges("generate_subqueries", continue_to_search, ["execute_search"])
    graph.add_edge("execute_search", "wait_for_searches")
    graph.add_conditional_edges("wait_for_searches", can_advance_after_search, {
        "go": "select_sources_to_read",  
        "wait": "wait_for_searches" # Retry until all expected finishes
    })
    
    # Read Phase 
    graph.add_conditional_edges("select_sources_to_read", continue_to_read, ["read_selected_sources"])
    graph.add_edge("read_selected_sources", "wait_for_reads")
    graph.add_conditional_edges("wait_for_reads", can_advance_after_read, {
        "go": "synthesize_draft",
        "wait": "wait_for_reads"
    })
    
    graph.add_edge("synthesize_draft", "evaluate_draft")
    
    # Loop or Finish
    graph.add_conditional_edges("evaluate_draft", should_continue, {
        "loop": "generate_subqueries",
        "stop": "output_results"
    })

    graph.add_edge("output_results", "download_the_report")
    graph.add_edge("download_the_report", END)
    
    # For LangGraph Studio, it prefers injecting its own checkpointer
    return graph.compile()

# Export the compiled graph for LangGraph Studio (langgraph dev)
app = build_graph()

def run_deep_research(question: str, max_iterations: int = 2) -> Dict[str, Any]:
    """
    Runner for our agent.
    """
    if not app:
        return {"answer": "Graph failed to compile"}
        
    state: ResearchState = {
        "question": question,
        "email": "",
        "plan": "",
        "subqueries": [],
        "next_subqueries": [],
        "searches": [],
        "docs": [],
        "notes": [],
        "answer_draft": "",
        "citations": [],
        "iteration": 0,
        "max_iterations": max_iterations,
        "done": False,
        "search_round": 0,
        "expected_search": 0,
        "search_marks": [],
        "read_round": 0,
        "expected_read": 0,
        "read_marks": []
    }
    
    config = {"configurable": {"thread_id": "deep-research"}}
    
    # Loop over the agent
    print(f"Starting research on: {question}")
    try:
        while True:
            # Let LangGraph coordinate iterations and loops
            state = app.invoke(state, config=config)
            if state.get("done"):
                break
                
        # Final answer formulation
        final = (state.get("answer_draft", "")).rstrip()
        citations = state.get("citations", [])
        
        if "References" not in final and citations:
            refs = "\n".join([f"[{i+1}] {u}" for i, u in enumerate(citations)])
            final += "\n\nReferences\n" + refs
            
        return {
            "answer": final,
            "plan": state.get("plan", ""),
            "sources": citations[:20]
        }
    except Exception as e:
        print(f"Error during runtime: {e}")
        return {"answer": "Agent run failed."}

if __name__ == "__main__":
    import sys
    # Take query from command line execution
    query = " ".join(sys.argv[1:]).strip() or "What is Agentic AI?"
    
    # Execute
    result = run_deep_research(query)
    
    # Output rendering (simple wrapper)
    print("\n" + "="*80)
    print("FINAL ANSWER\n")
    print(result.get("answer", ""))
    print("\n" + "="*80)
    print("PLAN\n")
    print(result.get("plan", ""))
    print("\nSOURCES")
    for s in result.get("sources", []):
        print(f"- {s}")
