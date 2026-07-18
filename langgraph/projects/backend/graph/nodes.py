from langgraph.prebuilt import ToolNode


from llm.llm import llm_with_tools


from tools.math_tool import calculator
from tools.time_tool import get_current_time
from tools.web_service import web_search




# Assistant Node
def assistant(state):


    messages = state["messages"]


    response = llm_with_tools.invoke(messages)


    return {
        "messages": [response]
    }




# Tool Node
tool_node = ToolNode(
    [
        calculator,
        get_current_time,
        web_search
    ]
)
