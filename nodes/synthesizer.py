import json
import re
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.graph import END

from state.state import ResearchState, SynthesizeOutput, ReflectionOutput
from utility.llm import get_llm
from utility.prompts import load_prompt

SYNTHESIZE_TEMPLATE = load_prompt("synthesize_prompt.txt")
REFLECT_TEMPLATE = load_prompt("reflect_prompt.txt")
SYSTEM_BRIEF = load_prompt("system_brief.txt")

PROMPT_SYNTHESIZE = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_BRIEF),
    ("human", SYNTHESIZE_TEMPLATE)
])

PROMPT_REFLECT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_BRIEF),
    ("human", REFLECT_TEMPLATE)
])

def node_synthesize(state: ResearchState) -> Dict[str, Any]:
    """
    Synthesize all search and read artifacts into a concise draft.
    """
    print("[synthesizer] Synthesizing final answer draft...")
    
    digests = []
    
    try:
        for d in state.get("docs", []):
            bullets = [
                b.strip("-• ") 
                for b in re.split(r"[\r\n]+", d.get("summary", "")) 
                if b.strip()
            ]
            digests.append({
                "url": d.get("url"), 
                "title": d.get("title"), 
                "key_points": bullets[:10]
            })
            
        parser = PydanticOutputParser(pydantic_object=SynthesizeOutput)
        llm = get_llm(temperature=0.2)
        chain = PROMPT_SYNTHESIZE | llm | parser
        
        result = chain.invoke({
            "question": state.get("question", ""),
            "notes": "\n".join(state.get("notes", []))[:4000],
            "digests": json.dumps(digests, ensure_ascii=False)[:15000]
        })
        
        # Track URLs used to generate citations list
        urls_in_order = []
        for d in state.get("docs", []):
            if d.get("url") and d["url"] not in urls_in_order:
                urls_in_order.append(d["url"])
                
        return {
            "citations": urls_in_order, 
            "answer_draft": result.answer_draft
        }
    except Exception as e:
        print(f"Error in synthesizer: {e}")
        return {
            "answer_draft": f"Failed to synthesize output due to error: {e}"
        }

def node_reflect(state: ResearchState) -> Dict[str, Any]:
    """
    Reflect on the drafted answer, proposing gaps and followups.
    """
    print("[synthesizer] Reflecting on answer...")
    
    try:
        parser = PydanticOutputParser(pydantic_object=ReflectionOutput)
        llm = get_llm(temperature=0.2)
        chain = PROMPT_REFLECT | llm | parser
        
        reflection = chain.invoke({
            "question": state.get("question", ""), 
            "answer_draft": state.get("answer_draft", "")
        })
        
        new_notes = []
        if reflection.gaps:
             new_notes.append("Gaps identified:\n- " + "\n- ".join(reflection.gaps[:5]))
        if reflection.followups:
             new_notes.append("Follow-up subqueries:\n- " + "\n- ".join(reflection.followups[:3]))
             
        # Increment iteration loop
        next_iter = state.get("iteration", 0) + 1
        wants_continue = reflection.decision.lower() == "continue"
        under_cap = next_iter < state.get("max_iterations", 2)
        should_continue = wants_continue and under_cap
        
        delta: Dict[str, Any] = {
            "iteration": next_iter, 
            "done": not should_continue
        }
        if new_notes:
            delta["notes"] = new_notes
        if reflection.followups:
            delta["next_subqueries"] = reflection.followups[:3]
            
        print(f"[router] Next iteration: {next_iter}. Decision: {reflection.decision}. Done: {not should_continue}")
        return delta
        
    except Exception as e:
        print(f"Error in reflect node: {e}")
        return {
            "iteration": state.get("iteration", 0) + 1,
            "done": True
        }

def should_continue(state: ResearchState) -> str:
    """
    Barrier: checks whether to loop back to plan_node/subqueries or stop.
    """
    if state.get("done", True) or state.get("iteration", 0) >= state.get("max_iterations", 2):
        return "stop"
    return "loop"
