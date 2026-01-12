import os
from dotenv import load_dotenv
from graphs.agent_graph import create_graph
import uuid

load_dotenv()

def test_agent():
    print("Testing Autonomous Research Agent...")
    topic = "Benefits of AI in Healthcare"
    
    app = create_graph()
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "topic": topic,
        "messages": [],
        "research_data": [],
        "report_format": None 
    }
    
    print("1. Running until HITL...")
    events = list(app.stream(initial_state, config=config))
    for event in events:
        print(f"Event: {event.keys()}")
        
    state = app.get_state(config)
    print(f"State after run 1: Next={state.next}")
    
    assert state.next[0] == "hitl", "Agent did not stop at HITL"
    
    print("2. Providing 'md' format and resuming...")
    app.update_state(config, {"report_format": "md"})
    
    events_resume = list(app.stream(None, config=config))
    for event in events_resume:
        print(f"Resume Event: {event.keys()}")
        if "report" in event:
            print("Report node executed.")
            
    # Check if report file exists
    expected_file = "reports/Benefits_of_AI_in_Healthcare_report.md"
    if os.path.exists(expected_file):
        print(f"SUCCESS: Report found at {expected_file}")
    else:
        print(f"FAILURE: Report not found.")

if __name__ == "__main__":
    test_agent()
