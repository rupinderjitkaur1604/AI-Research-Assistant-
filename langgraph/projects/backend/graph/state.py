# graph/state.py
from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages




class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]
    file_path: Optional[str]