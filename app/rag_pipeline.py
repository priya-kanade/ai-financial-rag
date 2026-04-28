from app.retriever import load_vectorstore
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from app.llm import llm
load_dotenv()

def load_multiple_vectorstores(file_list):
    dbs = []

    for f in file_list:
        folder = f"upload_{f.replace('.pdf','')}"
        try:
            db = load_vectorstore(folder)
            dbs.append(db)
        except:
            print(f"⚠️ Missing DB for {f}")

    return dbs


def get_response(query, selected_file=None, mode_source="demo"):

    # 🔹 Detect intent
    query_lower = query.lower()

    if "risk" in query_lower:
        mode = "risk"
    elif "summary" in query_lower or "summarize" in query_lower:
        mode = "summary"
    else:
        mode = "full"

    # 🔥 Enhanced query (MOVED UP - IMPORTANT)
    enhanced_query = query + """
    income statement consolidated financial statements
    revenue revenues net income net earnings operating income
    financial results earnings report
    """

    # =========================
    # 🔹 LOAD + RETRIEVE DOCS
    # =========================

    docs = []

    if mode_source == "upload":

        # 🔥 MULTI FILE
        if isinstance(selected_file, list) and selected_file:
            dbs = load_multiple_vectorstores(selected_file)

            for db in dbs:
                docs.extend(db.similarity_search(enhanced_query, k=5))

        # 🔥 SINGLE FILE
        elif selected_file:
            folder = f"vectorstores/upload/upload_{selected_file.replace('.pdf','')}"
            db = load_vectorstore(folder)
            docs = db.similarity_search(enhanced_query, k=10)

        else:
            return "No uploaded file selected.", []

    # 🔥 DEMO MODE
    else:
        folder = f"vectorstores/demo/vectorstore_{selected_file.replace('.pdf','')}"
        db = load_vectorstore(folder)
        docs = db.similarity_search(enhanced_query, k=10)

    # =========================
    # 🔹 DEBUG
    # =========================
    print("Mode:", mode)
    print("Selected file:", selected_file)
    print("Docs retrieved:", len(docs))

    for d in docs:
        print("✅ USING:", d.metadata.get("source"))

    # =========================
    # 🔥 FALLBACK (FIXED)
    # =========================
    if not docs:
        print("⚠️ No docs → fallback")

        if mode_source == "upload" and isinstance(selected_file, list):
            dbs = load_multiple_vectorstores(selected_file)
            for db in dbs:
                docs.extend(db.similarity_search(enhanced_query, k=3))

        elif mode_source == "upload" and selected_file:
            folder = f"vectorstores/upload/upload_{selected_file.replace('.pdf','')}"
            docs = db.similarity_search(enhanced_query, k=5)

        else:
            db = load_vectorstore(f"vectorstore_{selected_file.replace('.pdf','')}")
            docs = db.similarity_search(enhanced_query, k=5)

    # =========================
    # 🔥 REMOVE DUPLICATES
    # =========================
    unique_docs = []
    seen = set()

    for d in docs:
        key = (d.metadata.get("source"), d.metadata.get("page"))
        if key not in seen:
            seen.add(key)
            unique_docs.append(d)

    docs = unique_docs

    # =========================
    # 🔥 FILTERING
    # =========================
    keywords = [
        "revenue", "revenues", "total revenue",
        "net income", "net earnings",
        "operating income", "operating profit",
        "income statement", "financial statements",
        "consolidated", "earnings",
        "$", "million", "billion", "year ended"
    ]

    filtered_docs = [
        d for d in docs
        if any(k in d.page_content.lower() for k in keywords)
    ]

    if len(filtered_docs) >= 3:
        docs = filtered_docs
    else:
        print("⚠️ Weak filtering → keeping original docs")

    # =========================
    # 🔥 RERANKING
    # =========================
    def score(doc):
        text = doc.page_content.lower()
        s = 0

        if "income statement" in text:
            s += 4
        if "consolidated" in text:
            s += 3
        if "revenue" in text:
            s += 2
        if "net income" in text:
            s += 2
        if "operating income" in text:
            s += 2
        if "$" in text:
            s += 1

        return s

    docs = sorted(docs, key=score, reverse=True)

    # =========================
    # 🔥 CONTEXT SIZE
    # =========================
    if mode == "summary":
        docs = docs[:6]
    elif mode == "risk":
        docs = docs[:5]
    else:
        docs = docs[:5]

    print("Final docs used:", len(docs))

    if not docs:
        return "No relevant data found.", []

    # =========================
    # 🔹 BUILD CONTEXT
    # =========================
    context = "\n\n".join([d.page_content[:1200] for d in docs])



    # =========================
    # 🔥 PROMPTS
    # =========================

    if mode == "risk":
        prompt = f"""
        You are a financial analyst.

        Extract key risks from the document: {selected_file}

        RULES:
        - Only use given context
        - Group similar risks
        - No repetition

        Context:
        {context}

        Output:
        Key Risks:
        - bullet points only
        """

    elif mode == "summary":
        prompt = f"""
        You are a senior financial analyst.

        The document belongs to: {selected_file}

        STRICT RULES:
        - Use ONLY given data
        - Do NOT guess
        - Do NOT mix companies

        OUTPUT:

        Key Metrics:
        - Revenue:
        - Net Income:
        - Operating Income:

        Financial Summary:
        - Bullet points (performance + trends)

        Simple Insights:
        - Is company growing?
        - Is profit strong?
        - Any concern?

        Context:
        {context}
        """

    else:
        prompt = f"""
        You are a financial analyst.

        Analyze ONLY this company: {selected_file}

        Context:
        {context}

        Output:
        Financial Health:
        Key Risks:
        Positive Signals:
        Insights:
        """

    # 🔹 LLM call
    response = llm.invoke(prompt)

    if hasattr(response, "content"):
        return response.content, docs
    else:
        return str(response), docs

def chat_with_document(query, selected_file=None, mode_source="demo"):
    
    # =========================
    # 🔹 LOAD VECTORSTORE
    # =========================
    if mode_source == "upload":
        if not selected_file:
            return "No uploaded file selected.", []
        folder = f"vectorstores/upload/upload_{selected_file.replace('.pdf','')}"
    else:
        folder = f"vectorstores/demo/vectorstore_{selected_file.replace('.pdf','')}"

    db = load_vectorstore(folder)

    # =========================
    # 🧠 INTENT DETECTION
    # =========================
    query_lower = query.lower()

    if any(k in query_lower for k in ["revenue", "income", "profit", "earnings"]):
        intent = "metric"
    elif "risk" in query_lower:
        intent = "risk"
    elif any(k in query_lower for k in ["summary", "overview"]):
        intent = "summary"
    else:
        intent = "general"

    # =========================
    # 🔍 MULTI-QUERY RETRIEVAL
    # =========================
    queries = [query]

    if intent == "metric":
        queries.extend([
            "total revenue consolidated income statement",
            "financial highlights total revenue",
            "company total revenues fiscal year",
            "net income operating income"
        ])

    docs = []
    for q in queries:
        docs.extend(db.similarity_search(q, k=4))

    # =========================
    # 🔄 REMOVE DUPLICATES
    # =========================
    unique_docs = []
    seen = set()

    for d in docs:
        key = d.page_content[:100]
        if key not in seen:
            seen.add(key)
            unique_docs.append(d)

    docs = unique_docs

    if not docs:
        return "Not found in the document.", []

    # =========================
    # 🎯 FILTER + RERANK (CRITICAL)
    # =========================
    if intent == "metric":
        filtered = []

        for d in docs:
            text = d.page_content.lower()

            # ❌ remove irrelevant
            if "deferred revenue" in text:
                continue
            if "segment" in text:
                continue
            if "geographic" in text:
                continue

            filtered.append(d)

        if filtered:
            docs = filtered

        # 🔥 scoring
        scored_docs = []

        for d in docs:
            text = d.page_content.lower()
            score = 0

            if "total revenue" in text or "total revenues" in text:
                score += 5
            if "consolidated" in text:
                score += 3
            if "income statement" in text:
                score += 3
            if "$" in text or "million" in text or "billion" in text:
                score += 2

            scored_docs.append((d, score))

        scored_docs = sorted(scored_docs, key=lambda x: x[1], reverse=True)
        docs = [d for d, s in scored_docs[:3]]

    # =========================
    # 🔹 CONTEXT
    # =========================
    context = "\n\n".join([d.page_content[:1200] for d in docs])

    # =========================
    # 🔥 PROMPTS
    # =========================
    if intent == "metric":
        prompt = f"""
You are a financial analyst.

Your task is to find ONLY the TOTAL REVENUE of the company.

STRICT RULES:
- ONLY return revenue
- DO NOT return:
  - equity
  - assets
  - liabilities
  - any other metric
- If revenue is NOT present in the context, return EXACTLY:
  "Not found in the document"

- Handle units correctly:
  - If "in thousands" → convert to billions/millions

FORMAT:
Answer: <value OR Not found in the document>
Source: <short line>

Context:
{context}

Question:
{query}
"""

    elif intent == "risk":
        prompt = f"""
        Identify key risks.

        RULES:
        - Bullet points
        - No repetition

        Context:
        {context}
        """

    elif intent == "summary":
        prompt = f"""
        Provide concise summary:
        - performance
        - trends
        - insights

        Context:
        {context}
        """

    else:
        prompt = f"""
        Answer based only on context.

        RULES:
        - concise
        - no guessing

        Context:
        {context}

        Question:
        {query}
        """

    # =========================
    # 🔹 LLM
    # =========================
    response = llm.invoke(prompt)

    response_text = response.content if hasattr(response, "content") else str(response)
     # =========================
# 🔹 SOURCE + PAGE
# =========================
    page_info = ""

    if docs:
        first_doc = docs[0]
        page = first_doc.metadata.get("page", "Unknown")
        source = first_doc.metadata.get("source", "Unknown")

        page_info = f"\n\n📄 Source: {source} | Page: {page}"

    return response_text + page_info, docs