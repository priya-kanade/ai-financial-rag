from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import shutil
import os
from typing import Optional
from typing import Union, List
from app.agents import financial_agent
from app.ingest import load_pdf, chunk_data
from app.retriever import create_vectorstore

app = FastAPI()

# 📦 Request schema
class QueryRequest(BaseModel):
    query: str
    selected_file: Optional[Union[str, List[str]]] = None
    mode_source: str = "demo"   # 🔥 NEW

# 🏠 Health check
@app.get("/")
def home():
    return {"status": "running"}

# 🔍 Analyze endpoint
@app.post("/analyze")
def analyze(request: QueryRequest):
    response, docs = financial_agent(
        request.query,
        request.selected_file,
        request.mode_source
    )

    return {
        "response": response,
        "sources": [
            {
                "page": d.metadata.get("page"),
                "file": d.metadata.get("source"),
                "snippet": d.page_content[:150]
            }
            for d in docs
        ]
    }

# 📤 Upload endpoint
UPLOAD_DIR = "uploaded_data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # ✅ Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 🔥 Ingest immediately
    docs = load_pdf(file_path)
    chunks = chunk_data(docs)

    # 🔥 Save in separate vectorstore (NO mixing)
    folder_name = f"upload_{file.filename.replace('.pdf','')}"
    create_vectorstore(chunks, path=folder_name)

    return {"message": "Uploaded & Ready!"}