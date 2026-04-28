import os
from app.ingest import load_pdf, chunk_data
from app.retriever import create_vectorstore

# =========================
# 🔹 PATH SETUP
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_DIR, "data")
VECTOR_BASE = os.path.join("vectorstores", "demo")  # 🔥 NEW STRUCTURE

files = [f for f in os.listdir(DATA_PATH) if f.endswith(".pdf")]

# =========================
# 🔹 PROCESS FILES
# =========================
for file in files:
    path = os.path.join(DATA_PATH, file)

    print(f"\n🔍 Processing: {file}")

    docs = load_pdf(path)
    print(f"   → Extracted pages: {len(docs)}")

    chunks = chunk_data(docs)
    print(f"   → Chunks: {len(chunks)}")

    # =========================
    # 🔥 SAVE IN STRUCTURED FOLDER
    # =========================
    folder_name = f"{VECTOR_BASE}/vectorstore_{file.replace('.pdf','')}"

    create_vectorstore(chunks, path=folder_name)

# =========================
# 🔹 DONE
# =========================
print("\n✅ All vectorstores created successfully!")

# Debug sample
if chunks:
    print("\n🔍 Sample metadata:", chunks[0]["metadata"])