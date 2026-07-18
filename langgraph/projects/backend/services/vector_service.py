from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


COLLECTION_NAME = "pdf_documents"
QDRANT_PATH = "./qdrant_index"


def get_client():
    return QdrantClient(path=QDRANT_PATH)


def create_vector_store(documents):

    print("STEP 1 : Chunking")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)
    print(f"Chunks Created = {len(chunks)}")

    print("STEP 2 : Creating Qdrant collection")

    client = get_client()

    # Create collection if it doesn't exist
    existing = [c.name for c in client.get_collections().collections]

    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=768,
                distance=Distance.COSINE
            )
        )

    print("STEP 3 : Embedding + Saving to Qdrant")

    vectorstore = QdrantVectorStore.from_documents(
        chunks,
        embeddings,
        collection_name=COLLECTION_NAME,
        url=None,
        path=QDRANT_PATH,
    )

    print("STEP 4 : Saved to", QDRANT_PATH)

    return vectorstore