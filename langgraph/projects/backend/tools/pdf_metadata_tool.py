import fitz  # PyMuPDF
from langchain_core.tools import tool
import os




@tool
def extract_pdf_metadata(file_path: str) -> dict:
    """
    Extract metadata from a PDF file: file size, page count,
    title, author, creation date, and detected headings.
    Use this when the user asks about PDF properties, structure,
    or headings — not for full text content.
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}


    doc = fitz.open(file_path)


    file_size_bytes = os.path.getsize(file_path)
    metadata = doc.metadata


    # Heuristic heading detection: collect font sizes across the doc,
    # treat spans with above-average size (and short line length) as headings
    font_sizes = []
    spans_data = []


    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text:
                        continue
                    font_sizes.append(span["size"])
                    spans_data.append({
                        "text": text,
                        "size": span["size"],
                        "bold": bool(span["flags"] & 2 ** 4),
                        "page": page.number + 1
                    })


    avg_size = sum(font_sizes) / len(font_sizes) if font_sizes else 0
    heading_threshold = avg_size * 1.15  # tune this if headings are missed/over-caught


    headings = [
        {"text": s["text"], "page": s["page"], "size": round(s["size"], 1)}
        for s in spans_data
        if s["size"] >= heading_threshold and len(s["text"]) < 120
    ]


    result = {
        "file_size_bytes": file_size_bytes,
        "file_size_kb": round(file_size_bytes / 1024, 2),
        "num_pages": doc.page_count,
        "title": metadata.get("title") or None,
        "author": metadata.get("author") or None,
        "creation_date": metadata.get("creationDate") or None,
        "producer": metadata.get("producer") or None,
        "headings": headings
    }


    doc.close()
    return result
