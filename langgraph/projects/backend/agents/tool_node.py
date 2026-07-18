from langchain_core.messages import ToolMessage

from tools.math_tool import calculator
from tools.time_tool import get_current_time
from tools.web_service import web_search
from tools.pdf_metadata_tool import extract_pdf_metadata
from tools.pdf_text_tool import extract_pdf_text
from tools.pdf_summary_tool import summarize_pdf
from tools.pdf_embedding_tool import embed_pdf, query_pdf_index


TOOLS = {
    "calculator": calculator,
    "get_current_time": get_current_time,
    "web_search": web_search,
    "extract_pdf_metadata": extract_pdf_metadata,
    "extract_pdf_text": extract_pdf_text,
    "summarize_pdf": summarize_pdf,
    "embed_pdf": embed_pdf,
    "query_pdf_index": query_pdf_index,
}


PDF_TOOLS = {
    "extract_pdf_metadata",
    "extract_pdf_text",
    "summarize_pdf",
    "embed_pdf",
    "query_pdf_index",
}


def tool_node(state):

    last_message = state["messages"][-1]

    tool_messages = []

    for tool_call in last_message.tool_calls:

        tool_name = tool_call["name"]

        args = tool_call["args"]

        print("=" * 60)
        print("Tool Selected :", tool_name)
        print("Original Args :", args)

        # Inject uploaded PDF path
        if tool_name in PDF_TOOLS:

            args["file_path"] = state.get("file_path")

            print("Injected file_path :", args["file_path"])

        tool = TOOLS[tool_name]

        result = tool.invoke(args)

        print("Tool Result :", result)

        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
            )
        )

    return {
        "messages": tool_messages
    }