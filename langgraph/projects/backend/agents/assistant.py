from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from llm.llm import llm_with_tools
from llm.base_llm import llm
import re


# ---------------- Typo Fixer ---------------- #

def fix_typos(text: str) -> str:
    response = llm.invoke([
        HumanMessage(
            content=f"""
Fix any spelling mistakes in this query.
Return ONLY the corrected query.

{text}
"""
        )
    ])
    return response.content.strip()


# ---------------- System Prompt ---------------- #

system_prompt = SystemMessage(
    content="""
You are an AI Research Assistant with access to tools.

Use tools whenever appropriate.

Available tools:
- calculator
- get_current_time
- web_search
- extract_pdf_metadata
- extract_pdf_text
- summarize_pdf
- embed_pdf
- query_pdf_index

Rules:
-Use the calculator ONLY when the user is asking to compute a mathematical expression.

Never call the calculator for text that merely contains numbers, dates, page numbers, years, durations, article numbers, section numbers, or lists.

Examples:

Use calculator:
- 25*16
- sqrt(144)
- 2^10

Do NOT use calculator:
- Explain Chapter 3
- Teach this in 3 minutes
- What happened in 2025?
- Article 21
- Page 10
- Use get_current_time for date/time.
- Use PDF tools only if the user is asking about an uploaded PDF.
- Use web_search for general knowledge and internet questions.
- Never answer from your own knowledge if a tool is appropriate.
"""
)


# ---------------- Keywords ---------------- #

TOOL_KEYWORDS = [
    "summarize",
    "summary",
    "summarise",
    "metadata",
    "author",
    "title",
    "pages",
    "size",
    "file size",
    "extract text",
    "raw text",
    "full text",
    "embed",
    "index",
]

PDF_KEYWORDS = [
    "what",
    "who",
    "when",
    "where",
    "why",
    "how",
    "explain",
    "define",
    "describe",
    "list",
    "name",
    "which",
    "tell me",
    "according",
    "mention",
    "act",
    "article",
    "schedule",
    "amendment",
    "constitution",
    "section",
    "chapter",
    "difference",
    "compare",
    "rights",
    "duties",
    "powers",
    "features",
]

WEB_KEYWORDS = [
    "langgraph",
    "langchain",
    "fastapi",
    "python",
    "javascript",
    "machine learning",
    "deep learning",
    "neural network",
    "llm",
    "docker",
    "kubernetes",
    "news",
    "latest",
    "today",
    "weather",
    "stock",
    "capital of",
    "population",
]


# ---------------- Math Detection ---------------- #

MATH_KEYWORDS = [
    "calculate",
    "solve",
    "evaluate",
    "sqrt",
    "square root",
    "factorial",
    "log",
    "sin",
    "cos",
    "tan",
]

MATH_EXPRESSION = re.compile(
    r"^\s*[\d\s+\-*/^().]+\s*$"
)


# ---------------- Assistant ---------------- #

def assistant_agent(state):

    last_message = state["messages"][-1].content
    file_path = state.get("file_path")

    # ---------------- Typo Fix ---------------- #

    corrected = fix_typos(last_message)

    if corrected != last_message:
        print(f"[Typo Fix] {last_message} -> {corrected}")

    last_message = corrected
    lower_msg = last_message.lower()

    is_tool_request = any(k in lower_msg for k in TOOL_KEYWORDS)
    is_web_question = any(k in lower_msg for k in WEB_KEYWORDS)

    # ---------------- Math Router ---------------- #

    is_math = (
        any(k in lower_msg for k in MATH_KEYWORDS)
        or bool(MATH_EXPRESSION.match(last_message.strip()))
    )

    if is_math:

        print("[MATH ROUTER]")

        from tools.math_tool import calculator

        result = calculator.invoke(
            {
                "expression": last_message
            }
        )

        return {
            "messages": [
                AIMessage(content=str(result))
            ]
        }

    # ---------------- Web Router ---------------- #

    if is_web_question and not is_tool_request:

        print("[WEB ROUTER]")

        from tools.web_service import web_search

        results = web_search.invoke(
            {
                "query": last_message
            }
        )

        prompt = f"""
Answer the question using these search results.

SEARCH RESULTS:
{results}

QUESTION:
{last_message}
"""

        response = llm.invoke(
            [
                HumanMessage(content=prompt)
            ]
        )

        return {
            "messages": [
                AIMessage(content=response.content)
            ]
        }

    # ---------------- PDF Router ---------------- #

    if (
        file_path
        and not is_tool_request
        and any(k in lower_msg for k in PDF_KEYWORDS)
    ):

        print("[PDF ROUTER]")

        from tools.pdf_embedding_tool import query_pdf_index

        chunks = query_pdf_index.invoke(
            {
                "file_path": file_path,
                "query": last_message,
            }
        )

        prompt = f"""
Answer ONLY from the provided context.

CONTEXT:
{chunks}

QUESTION:
{last_message}

If the answer is not present in the context, reply:
'I couldn't find this information in the uploaded PDF.'
"""

        response = llm.invoke(
            [
                HumanMessage(content=prompt)
            ]
        )

        return {
            "messages": [
                AIMessage(content=response.content)
            ]
        }

    # ---------------- Tool Router ---------------- #

    print("[LLM TOOL ROUTER]")

    messages = [
        system_prompt,
        *state["messages"],
    ]

    response = llm_with_tools.invoke(messages)

    print(response)
    print(response.tool_calls)

    return {
        "messages": [
            response
        ]
    }