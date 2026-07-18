from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
import os




@tool
def extract_pdf_text(file_path: str) -> str:
    """
    Extract full plain text content from a PDF file, page by page.
    Use this when the user wants the raw text/content of a PDF
    (e.g. to summarize, search, or embed it).
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"


    loader = PyPDFLoader(file_path)
    documents = loader.load()


    if not documents:
        return f"Error: No content could be extracted from {file_path}"


    pages_text = [
        f"--- Page {doc.metadata.get('page', i) + 1} ---\n{doc.page_content}"
        for i, doc in enumerate(documents)
    ]


    return "\n\n".join(pages_text)
