import os

from langchain_core.tools import tool
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ==========================================================
# EMBEDDING MODEL
# ==========================================================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("\n" + "=" * 60)
print("EMBEDDING MODEL LOADED")
print("=" * 60)
print("Model Name :", embeddings.model_name)

test_vector = embeddings.embed_query("Hello World")
print("Embedding Dimension :", len(test_vector))
print("=" * 60 + "\n")


# ==========================================================
# FAISS STORAGE
# ==========================================================

FAISS_INDEX_DIR = "faiss_indexes"


# ==========================================================
# EMBED PDF
# ==========================================================

@tool
def embed_pdf(file_path: str) -> dict:
    """
    Embed a PDF into a FAISS index.
    """

    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    print("STEP 1 : Loading PDF")

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    if not documents:
        return {"error": "No text found in PDF."}

    print(f"STEP 2 : Loaded {len(documents)} pages")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(documents)

    print(f"STEP 3 : Total Chunks = {len(chunks)}")

    if not chunks:
        return {"error": "Chunking failed."}

    print("STEP 4 : Creating FAISS Index")

    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    os.makedirs(FAISS_INDEX_DIR, exist_ok=True)

    pdf_name = os.path.splitext(
        os.path.basename(file_path)
    )[0]

    index_path = os.path.join(
        FAISS_INDEX_DIR,
        pdf_name
    )

    vectorstore.save_local(index_path)

    print("STEP 5 : FAISS Saved")
    print("FAISS Index Dimension :", vectorstore.index.d)

    return {
        "status": "success",
        "pages": len(documents),
        "chunks": len(chunks),
        "index_path": index_path
    }


# ==========================================================
# QUERY PDF
# ==========================================================

@tool
def query_pdf_index(
    file_path: str,
    query: str,
    k: int = 4
) -> str:
    """
    Query a FAISS index.
    """

    pdf_name = os.path.splitext(
        os.path.basename(file_path)
    )[0]

    index_path = os.path.join(
        FAISS_INDEX_DIR,
        pdf_name
    )

    # Auto embed if index not found
    if not os.path.exists(index_path):

        print("FAISS Index Not Found")

        result = embed_pdf.invoke(
            {"file_path": file_path}
        )

        if "error" in result:
            return result["error"]

    print("Loading FAISS...")

    vectorstore = FAISS.load_local(
        folder_path=index_path,
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )

    print("\n" + "=" * 60)
    print("DEBUG INFORMATION")
    print("=" * 60)

    query_vector = embeddings.embed_query(query)

    print("Embedding Model :", embeddings.model_name)
    print("Query           :", query)
    print("Query Dimension :", len(query_vector))
    print("FAISS Dimension :", vectorstore.index.d)

    if len(query_vector) == vectorstore.index.d:
        print("✅ Dimensions Match")
    else:
        print("❌ Dimension Mismatch")
        print("Query Vector Size :", len(query_vector))
        print("FAISS Index Size  :", vectorstore.index.d)

    print("=" * 60 + "\n")

    print("Searching...")

    docs = vectorstore.similarity_search(
        query=query,
        k=k
    )

    if not docs:
        return "No relevant information found."

    answer = ""

    for i, doc in enumerate(docs, start=1):

        page = doc.metadata.get("page", "Unknown")

        answer += (
            f"\n===== Result {i} =====\n"
            f"Page : {page}\n\n"
            f"{doc.page_content}\n"
        )

    return answer