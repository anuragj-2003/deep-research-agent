import time
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.types import Send, Command

from state.state import ResearchState, DocSummaryOutput
from utility.llm import get_llm
from utility.prompts import load_prompt
from utility.fetch import web_fetch

SUMMARY_TEMPLATE = load_prompt("doc_summary_prompt.txt")
SYSTEM_BRIEF = load_prompt("system_brief.txt")

PROMPT_DOC_SUMMARY = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_BRIEF),
    ("human", SUMMARY_TEMPLATE)
])

def plan_reads(state: ResearchState):
    """
    Plans which docs to read by firing off read workers.
    """
    # Limit to top 3 instead of 10 to reduce parallel Groq requests (rate limits)
    top = state.get("searches", [])[:3]
    next_round = state.get("read_round", 0) + 1
    
    print(f"[reader] Dispatching {len(top)} reads for round {next_round}...")
    
    return {
        "read_round": next_round,
        "expected_read": len(top)
    }

def continue_to_read(state: ResearchState):
    """Routing function to fan-out read workers"""
    top = state.get("searches", [])[:3]
    next_round = state.get("read_round", 0)
    return [
        Send("read_selected_sources", {
            "url": h["url"], 
            "question": state["question"], 
            "round": next_round
        }) for h in top
    ]

def read_worker(arg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetches the content from URL and generates a summary via LLM.
    """
    url = arg.get("url", "")
    question = arg.get("question", "")
    round_id = arg.get("round", 0)
    
    print(f"[reader] Fetching and summarizing {url}...")
    
    doc = web_fetch(url)
    if not doc or not doc.get("content"):
        # Failed fetch or empty content
        return {"docs": [], "read_marks": [round_id]}
        
    try:
        llm = get_llm(temperature=0.1)
        parser = PydanticOutputParser(pydantic_object=DocSummaryOutput)
        chain = PROMPT_DOC_SUMMARY | llm | parser
        
        summary_obj = chain.invoke({
            "question": question,
            "title": doc["title"],
            "url": doc["url"],
            "content": doc["content"][:12000] # Truncate for token limits
        })
        
        import random
        # Stagger requests slightly to help with rate limits
        time.sleep(random.uniform(1.0, 3.0))
        
        doc["summary"] = summary_obj.summary
        
        # Be gentle
        time.sleep(1.0)
        
        return {"docs": [doc], "read_marks": [round_id]}
    except Exception as e:
        print(f"Error summarizing content for {url}: {e}")
        return {"docs": [], "read_marks": [round_id]}

def read_join(state: ResearchState) -> Dict[str, Any]:
    """
    Aggregates the read results taking the top 5 to avoid blowing up context window.
    """
    print("[reader] Joining read results...")
    docs = state.get("docs", [])
    
    # Optional logic: Deduplicate by URL or keep top 5
    return {"docs": docs[:5]}

def can_advance_after_read(state: ResearchState) -> str:
    """
    Barrier for read fan-out. Wait until marks == expected.
    """
    expected = state.get("expected_read", 0)
    current_round = state.get("read_round", 0)
    marks = state.get("read_marks", [])
    
    done = sum(1 for rid in marks if rid == current_round)
    print(f"[router] Read barrier: {done}/{expected} workers done.")
    
    if expected == 0 or done >= expected:
        return "go"
    else:
        return "wait"
