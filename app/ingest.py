import pdfplumber
import camelot
import os
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter


# =========================
# 🔹 CLEAN TEXT
# =========================
def clean_text(text):
    if not text:
        return ""

    text = re.sub(r'\b(b\s*i\s*l\s*l\s*i\s*o\s*n)\b', 'billion', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(m\s*i\s*l\s*l\s*i\s*o\s*n)\b', 'million', text, flags=re.IGNORECASE)
    text = re.sub(r'(\d)\s*,\s*(\d)', r'\1,\2', text)
    text = re.sub(r'(\d)\s*\.\s*(\d)', r'\1.\2', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# =========================
# 🔹 LOAD PDF
# =========================
def load_pdf(file_path):
    docs = []
    filename = os.path.basename(file_path)

    # -------------------------
    # 🔥 RUN CAMELOT ONCE
    # -------------------------
    try:
        print("🔍 Extracting tables (Camelot)...")
        camelot_tables = camelot.read_pdf(file_path, pages='all')
        print(f"   → Tables found: {len(camelot_tables)}")
    except Exception as e:
        print("⚠️ Camelot failed, continuing without tables")
        camelot_tables = []

    # Map tables by page
    tables_by_page = {}

    for table in camelot_tables:
        page_num = int(table.page)
        tables_by_page.setdefault(page_num, []).append(table)

    # -------------------------
    # TEXT EXTRACTION
    # -------------------------
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_num = i + 1
            print(f"Processing page {page_num}/{len(pdf.pages)}")

            text = page.extract_text() or ""
            text = clean_text(text)

            # -------------------------
            # 🔥 TABLE EXTRACTION (FAST)
            # -------------------------
            table_text = ""

            if page_num in tables_by_page:
                for table in tables_by_page[page_num]:
                    df = table.df

                    headers = df.iloc[0]

                    for idx in range(1, len(df)):
                        row = df.iloc[idx]

                        row_pairs = []
                        for col_idx, cell in enumerate(row):
                            key = str(headers[col_idx]).strip()
                            value = str(cell).strip()

                            if key and value and value.lower() != "nan":
                                row_pairs.append(f"{key}: {value}")

                        if row_pairs:
                            table_text += " ; ".join(row_pairs) + "\n"

            # -------------------------
            # COMBINE
            # -------------------------
            full_text = f"{text}\n\n[FINANCIAL TABLE DATA]\n{table_text}"

            # Boost importance
            full_text = full_text + "\n\n[IMPORTANT FINANCIAL DATA]\n" + full_text

            # -------------------------
            # FILTER
            # -------------------------
            if len(full_text.strip()) < 200:
                continue

            if not re.search(r'\d', full_text):
                continue

            docs.append({
                "text": full_text,
                "metadata": {
                    "page": page_num,
                    "source": filename
                }
            })

    return docs


# =========================
# 🔹 CHUNKING
# =========================
def chunk_data(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200
    )

    chunks = []

    for doc in docs:
        splits = splitter.split_text(doc["text"])

        for chunk in splits:
            if len(chunk.strip()) < 100:
                continue

            chunks.append({
                "text": chunk,
                "metadata": doc["metadata"]
            })

    return chunks