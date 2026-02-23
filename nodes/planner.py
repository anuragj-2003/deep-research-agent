from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.types import Send, Command

from state.state import ResearchState, PlanOutput, SubqueriesOutput
from utility.llm import get_llm
from utility.prompts import load_prompt

# Dynamically load templates
SYSTEM_BRIEF = load_prompt("system_brief.txt")
PLAN_TEMPLATE = load_prompt("plan_prompt.txt")
SUBQUERIES_TEMPLATE = load_prompt("subqueries_prompt.txt")

# Set up prompts
PROMPT_PLAN = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_BRIEF),
    ("human", PLAN_TEMPLATE)
])

PROMPT_SUBQUERIES = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_BRIEF),
    ("human", SUBQUERIES_TEMPLATE)
])

def node_plan(state: ResearchState) -> Dict[str, Any]:
    """
    Drafts the initial research plan.
    """
    print("[planner] Drafting research plan...")
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=PlanOutput)
    chain = PROMPT_PLAN | llm | parser
    
    try:
        result = chain.invoke({"question": state["question"]})
        return {"plan": result.plan, "notes": [f"Plan:\n{result.plan}"]}
    except Exception as e:
        print(f"Error in node_plan: {e}")
        return {"plan": "Fallback plan due to error.", "notes": [f"Error: {e}"]}

def node_subqueries(state: ResearchState):
    """
    Proposes subqueries to execute. Uses previous follow-ups if available.
    """
    print("[planner] Generating subqueries...")
    
    subqs = []
    try:
        # Use existing follow-ups if they were generated during Reflection
        if state.get("next_subqueries"):
            subqs = [q.strip() for q in state["next_subqueries"] if q.strip()]
        else:
            llm = get_llm()
            parser = PydanticOutputParser(pydantic_object=SubqueriesOutput)
            chain = PROMPT_SUBQUERIES | llm | parser
            
            result = chain.invoke({
                "question": state["question"], 
                "plan": state["plan"]
            })
            
            seen = set()
            for q in result.subqueries:
                q = q.strip()
                if q and q not in seen:
                    seen.add(q)
                    subqs.append(q)
                if len(subqs) >= 3: # Limit to 3
                    break
    except Exception as e:
        print(f"Error in node_subqueries: {e}")
        subqs = ["Agentic AI overview", "Deep Research AI examples"]

    # Increment round
    next_round = state.get("search_round", 0) + 1
    
    return {
        "subqueries": subqs,
        "next_subqueries": [], # Clear followups
        "search_round": next_round,
        "expected_search": len(subqs)
    }

def continue_to_search(state: ResearchState):
    """Routing function to fan-out search workers"""
    next_round = state.get("search_round", 0)
    subqs = state.get("subqueries", [])
    return [Send("execute_search", {"q": q, "round": next_round}) for q in subqs]
