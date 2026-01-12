from typing import List, Dict, Any, Optional, Annotated
from pydantic import BaseModel, Field, ConfigDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class InputState(BaseModel):
    """
    Input schema defining what the user sees in the UI.
    """
    messages: List[BaseMessage] = Field(default_factory=list)
    topic: Optional[str] = Field(default=None, description="The research topic")

class AgentState(BaseModel):
    """
    Unified state for the Autonomous Research Agent.
    """
    model_config = ConfigDict(
        extra="ignore", # Ignore extra fields
        arbitrary_types_allowed=True,
    )

    # Core Messaging
    messages: Annotated[List[BaseMessage], add_messages] = Field(default_factory=list)
    
    # Data
    topic: str = Field(default="", description="The research topic")
    research_data: List[dict] = Field(default_factory=list)
    summary: Optional[str] = None
    
    # Report Config
    report_format: Optional[str] = None # 'pdf', 'ppt', 'md', 'docx'
    report_content: Optional[str] = None
    email: Optional[str] = None
    
    # Methods for State Compatibility (Dict-like access)
    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)
