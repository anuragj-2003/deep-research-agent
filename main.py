import uuid
from langchain_core.messages import HumanMessage
from graphs.agent_graph import create_graph
from states.state import AgentState, InputState

def main():
    print("Welcome to the Autonomous Research Agent")
    user_input = input("Enter your research request (e.g. 'Research AI and send pdf to me@example.com'): ")
    
    # Create the graph
    app = create_graph()
    
    # Initial state
    initial_state = {
        "messages": [HumanMessage(content=user_input)]
    }
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"Starting research on: {topic}...")
    
    # First run - will stop at hitl if format is missing
    for event in app.stream(initial_state, config=config):
        for key, value in event.items():
            print(f"-- Node: {key} --")
            if "summary" in value:
                print("Summary generated.")
            if "messages" in value:
                # Print last message
                pass

    # Check state to see if we are at HITL
    state_snapshot = app.get_state(config)
    if state_snapshot.next:
        if state_snapshot.next[0] == "hitl":
            print("\n!!! Interrupt: Missing Report Format !!!")
            user_choice = input("Please choose format (pdf, ppt, md): ").strip().lower()
            
            # Update state with user choice
            app.update_state(config, {"report_format": user_choice})
            
            print(f"Resuming with format: {user_choice}...")
            # Resume
            for event in app.stream(None, config=config):
                 for key, value in event.items():
                    print(f"-- Node: {key} --")
                    if "report_content" in value:
                        print("Report generated successfully!")

if __name__ == "__main__":
    main()
