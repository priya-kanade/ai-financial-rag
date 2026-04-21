# 📊 AI Financial Intelligence Platform

An end-to-end AI system that analyzes financial reports (PDFs) using **Retrieval-Augmented Generation (RAG)** and **MapReduce summarization**, providing structured insights like revenue trends, profitability, and risk analysis.

---

## 🚀 Overview

Financial reports are long, complex, and difficult to analyze manually.
This project solves that by building an **AI-powered financial analyst** that can:

* 📄 Understand 100+ page annual reports
* 📊 Extract key financial metrics
* ⚠️ Identify business risks
* 💡 Generate clear insights for decision-making

---

## ✨ Key Features

### 🔍 Intelligent Document Analysis

* Processes large financial PDFs (annual reports, filings)
* Extracts structured insights using LLMs

### 📊 Financial Summary (MapReduce)

* Full-document understanding (not just chunks)
* Extracts:

  * Revenue
  * Net Income
  * Operating Income
  * Multi-year trends

### ⚠️ Risk Detection

* Identifies and groups key business risks
* Removes redundancy and noise

### 🤖 RAG-based Q&A

* Ask custom questions about reports
* Retrieves relevant context dynamically

### 📂 Multi-PDF Support

* Upload multiple reports
* Query across documents (RAG)
* Single-document deep analysis (MapReduce)

### 🎯 Smart Hybrid System

* MapReduce for full summaries
* RAG fallback if data is missing
* Ensures higher accuracy and reliability

---

## 🧠 System Architecture

```text
User Query / Action
        ↓
   Agent Layer
 (Intent Detection)
        ↓
 ┌───────────────┐
 │   MapReduce   │ ← Full document summary
 └───────────────┘
        ↓ (fallback)
 ┌───────────────┐
 │      RAG      │ ← Targeted retrieval
 └───────────────┘
        ↓
   LLM (Groq / LLaMA 3)
        ↓
 Structured Output (UI)
```

---

## 🛠 Tech Stack

| Category       | Tools                |
| -------------- | -------------------- |
| Backend        | FastAPI              |
| Frontend       | Streamlit            |
| LLM            | Groq (LLaMA 3)       |
| Embeddings     | HuggingFace (MiniLM) |
| Vector DB      | FAISS                |
| PDF Processing | pdfplumber           |
| Framework      | LangChain            |

---

## 📁 Project Structure

```text
ai-financial-rag/
│── app/
│   ├── api.py
│   ├── agents.py
│   ├── rag_pipeline.py
│   ├── map_reduce.py
│   ├── ingest.py
│   ├── retriever.py
│
│── data/                # Demo PDFs
│── uploaded_data/       # User uploads
│── vectorstore_*        # Demo vector DBs
│── upload_*             # Upload vector DBs
│
│── app.py               # Streamlit UI
│── requirements.txt
│── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/priya-kanade/ai-financial-rag.git
cd ai-financial-rag
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Add Environment Variables

Create `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

---

## ▶️ Running the Application

### 🔹 Start Backend

```bash
uvicorn app.api:app --reload
```

---

### 🔹 Start Frontend

```bash
streamlit run app.py
```

---

## 💻 Usage

### 📂 Demo Mode

* Select preloaded financial reports
* Run summary or risk analysis

### 📤 Upload Mode

* Upload your own PDF
* Analyze instantly

---

### ⚡ Available Actions

* 📊 **Summarize Report**
* ⚠️ **Find Risks**
* 💬 **Ask Custom Questions**

---

## 📊 Example Output

### Key Metrics

* Revenue: $107.3B (2024)
* Net Income: $7.15B (↓ YoY)
* Operating Income: Declining trend

### Financial Summary

* Revenue increased but margins declined
* Profitability weakened due to cost pressure

### Insights

* Growth in top-line but declining efficiency
* Competitive pressure impacting margins

---

## ⚠️ Limitations

* MapReduce works on **single document only**
* Accuracy depends on PDF structure quality
* Complex tables may require better parsing

---

## 🚀 Future Improvements

* 📈 KPI visualization (charts)
* 📊 Better table extraction (Camelot/Tabula)
* 🧠 Financial ratio calculations
* 🌐 Deployment (Streamlit Cloud / AWS)
* 🔎 Semantic search optimization

---

## 🧑‍💻 Author

**Priya Kanade**


---

## ⭐ Why This Project Stands Out

* Combines **RAG + MapReduce** (advanced architecture)
* Handles **real-world financial documents**
* Supports **multi-document workflows**
* Focuses on **practical business insights**

---

## 📌 Final Note

This project is designed to simulate a **real-world AI financial analyst system**, bridging the gap between raw data and actionable insights.

---
