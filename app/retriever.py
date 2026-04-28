from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os

# Project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# =========================
# 🔹 EMBEDDINGS
# =========================
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# =========================
# 🔹 BUILD PATH
# =========================
def build_path(path):
    full_path = os.path.join(BASE_DIR, path)

    # create folder if not exists
    os.makedirs(full_path, exist_ok=True)

    return full_path


# =========================
# 🔹 CREATE VECTORSTORE
# =========================
def create_vectorstore(chunks, path="vectorstores/demo/default"):
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    embeddings = get_embeddings()

    db = FAISS.from_texts(
        texts,
        embeddings,
        metadatas=metadatas
    )

    save_path = build_path(path)
    db.save_local(save_path)

    return db


# =========================
# 🔹 LOAD VECTORSTORE
# =========================
def load_vectorstore(path="vectorstores/demo/default"):
    embeddings = get_embeddings()

    load_path = os.path.join(BASE_DIR, path)

    if not os.path.exists(load_path):
        raise ValueError(f"Vectorstore not found at {load_path}")

    return FAISS.load_local(
        load_path,
        embeddings,
        allow_dangerous_deserialization=True
    )