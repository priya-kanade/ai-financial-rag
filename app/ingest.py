
import pdfplumber
import os
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter


def clean_text(text):
    if not text:
        return ""

    # ✅ fix spaced million/billion safely
    text = re.sub(r'\b(b\s*i\s*l\s*l\s*i\s*o\s*n)\b', 'billion', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(m\s*i\s*l\s*l\s*i\s*o\s*n)\b', 'million', text, flags=re.IGNORECASE)

    # ✅ fix comma spacing
    text = re.sub(r'(\d)\s*,\s*(\d)', r'\1,\2', text)

    # ✅ fix spaced decimals
    text = re.sub(r'(\d)\s*\.\s*(\d)', r'\1.\2', text)

    # ✅ remove extra spaces only
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def load_pdf(file_path):
    docs = []
    filename = os.path.basename(file_path)

    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""

            text = clean_text(text)

            # 🔥 Extract tables
            tables = page.extract_tables()
            table_text = ""

            for table in tables:
                for row in table:
                    row_text = " | ".join([str(cell) if cell else "" for cell in row])
                    table_text += row_text + "\n"

            full_text = f"{text}\n\n[TABLE DATA]\n{table_text}"

            # ✅ LIGHT FILTER (NOT aggressive)
            if len(full_text.strip()) < 200:
                continue  # skip empty/noisy pages only

            docs.append({
                "text": full_text,
                "metadata": {
                    "page": i + 1,
                    "source": filename
                }
            })

    return docs

def chunk_data(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,     # 🔥 bigger = better table context
        chunk_overlap=200    # 🔥 preserves continuity
    )

    chunks = []

    for doc in docs:
        splits = splitter.split_text(doc["text"])

        for chunk in splits:
            chunks.append({
                "text": chunk,
                "metadata": doc["metadata"]
            })

    return chunks