from llm.base_llm import llm

from tools.math_tool import calculator
from tools.time_tool import get_current_time
from tools.web_service import web_search
from tools.pdf_metadata_tool import extract_pdf_metadata
from tools.pdf_text_tool import extract_pdf_text
from tools.pdf_summary_tool import summarize_pdf
from tools.pdf_embedding_tool import (
    embed_pdf,
    query_pdf_index,
)

# -------------------------------------------------------
# Bind all tools to the LLM
# -------------------------------------------------------

TOOLS = [
    calculator,
    get_current_time,
    web_search,
    extract_pdf_metadata,
    extract_pdf_text,
    summarize_pdf,
    embed_pdf,
    query_pdf_index,
]

llm_with_tools = llm.bind_tools(TOOLS)