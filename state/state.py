from typing import TypedDict, Annotated, List, Any
from operator import add
from pydantic import BaseModel

class Doc(TypedDict):
    url: str
    title: str
    summary: str
    content: str

from typing_extensions import NotRequired

class SearchHit(TypedDict):
    query: str
    url: str
    title: str
    snippet: str

class InputState(TypedDict):
    question: str

class ResearchState(TypedDict):
    # Core
    question: str
    email: NotRequired[str]
    plan: str

    # Iteration query ownership
    subqueries: List[str]
    next_subqueries: List[str]

    # Aggregates (Parallel Reducers)
    searches: Annotated[List[SearchHit], add]
    docs: Annotated[List[Doc], add]
    notes: Annotated[List[str], add]

    # Outputs
    answer_draft: str
    citations: List[str]

    # Loop Control
    iteration: int
    max_iterations: int
    done: bool

    # Barriers (Round-scoped)
    search_round: int
    expected_search: int
    search_marks: Annotated[List[int], add]

    read_round: int
    expected_read: int
    read_marks: Annotated[List[int], add]

# -----------------
# Pydantic Outputs
# -----------------

class PlanOutput(BaseModel):
    plan: str

class SubqueriesOutput(BaseModel):
    subqueries: List[str]

class DocSummaryOutput(BaseModel):
    summary: str

class SynthesizeOutput(BaseModel):
    answer_draft: str

class ReflectionOutput(BaseModel):
    gaps: List[str]
    followups: List[str]
    decision: str
    why: str
