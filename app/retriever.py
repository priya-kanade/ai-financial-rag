from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os
from app.ingest import load_pdf, chunk_data
# Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def create_vectorstore(chunks, path="vectorstore"):
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    embeddings = get_embeddings()

    db = FAISS.from_texts(
        texts,
        embeddings,
        metadatas=metadatas
    )

    # 🔥 dynamic path (important)
    save_path = os.path.join(BASE_DIR, path)

    db.save_local(save_path)

    return db


def load_vectorstore(path="vectorstore"):
    embeddings = get_embeddings()

    return FAISS.load_local(
        os.path.join(BASE_DIR, path),
        embeddings,
        allow_dangerous_deserialization=True
    )

