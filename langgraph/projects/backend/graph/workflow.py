from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langgraph.prebuilt import tools_condition


from graph.state import ResearchState


from agents.assistant import assistant_agent
from agents.tool_node import tool_node




builder = StateGraph(ResearchState)


builder.add_node(
    "assistant",
    assistant_agent
)


builder.add_node(
    "tools",
    tool_node
)


builder.add_edge(
    START,
    "assistant"
)


builder.add_conditional_edges(
    "assistant",
    tools_condition
)


builder.add_edge(
    "tools",
    "assistant"
)


builder.add_edge(
    "assistant",
    END
)


app = builder.compile()