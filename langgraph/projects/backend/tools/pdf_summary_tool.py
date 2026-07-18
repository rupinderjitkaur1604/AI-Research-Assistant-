from langchain_core.tools import tool
from llm.base_llm import llm  # plain ChatOllama instance, NOT the one bound with tools
from tools.pdf_text_tool import extract_pdf_text




@tool
def summarize_pdf(file_path: str) -> str:
    """
    Generate a concise summary of a PDF's content.
    Use this when the user asks to summarize a PDF document.
    """
    text = extract_pdf_text.invoke({"file_path": file_path})


    if text.startswith("Error"):
        return text


    # qwen2.5:3b has a limited context window — truncate defensively
    max_chars = 1200
    truncated = text[:max_chars]


    prompt = f"""Summarize the following document in 5-8 concise bullet points.
Focus on key ideas, not filler.


DOCUMENT:
{truncated}
"""


    response = llm.invoke(prompt)
    return response.content
