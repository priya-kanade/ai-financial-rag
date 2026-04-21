import os
from app.ingest import load_pdf, chunk_data
from app.retriever import create_vectorstore

# Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data")

files = [f for f in os.listdir(DATA_PATH) if f.endswith(".pdf")]

for file in files:
    path = os.path.join(DATA_PATH, file)

    print(f"\n🔍 Processing: {file}")

    docs = load_pdf(path)

    print(f"   → Extracted pages: {len(docs)}")

    chunks = chunk_data(docs)

    print(f"   → Chunks: {len(chunks)}")

    # 🔥 SAVE SEPARATE VECTORSTORE
    folder_name = f"vectorstore_{file.replace('.pdf','')}"

    create_vectorstore(chunks, path=folder_name)

print("\n✅ All vectorstores created separately!")

print("\n✅ FAISS index created successfully!")

# Debug sample
print("\n🔍 Sample metadata:", chunks[0]["metadata"])