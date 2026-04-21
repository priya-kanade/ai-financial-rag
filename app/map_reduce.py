
import time
from app.retriever import load_vectorstore
from app.llm import llm


def map_reduce_summary(selected_file=None, mode_source="demo"):

    if not selected_file:
        return "No file selected for summary.",[]
    
    # 🔥 HANDLE LIST (CRITICAL FIX)
    if isinstance(selected_file, list):
        if len(selected_file) == 0:
            return "No file selected.", []
        selected_file = selected_file[0]   # take first file

    # 🔥 DEMO MODE
    if mode_source == "demo":
        folder = f"vectorstore_{selected_file.replace('.pdf','')}"
    
    # 🔥 UPLOAD MODE
    else:
        folder = f"upload_{selected_file.replace('.pdf','')}"

    db = load_vectorstore(folder)

    # 🔥 Step 1: Retrieve more docs
    docs = db.similarity_search(
        "income statement revenue net income operating income financial results",
        k=50
    )

    # 🔹 Filter by selected file
    if selected_file:
        docs = [
            d for d in docs
            if selected_file.lower() in d.metadata.get("source", "").lower()
        ]

    if not docs:
        return "No data found for this document.", []

    # 🔥 Step 2: Soft financial filtering (NOT strict)
    keywords = [
        "revenue", "net income", "operating income",
        "income statement", "financial", "earnings",
        "$", "million", "billion", "year ended"
    ]

    financial_docs = [
        d for d in docs
        if any(k in d.page_content.lower() for k in keywords)
    ]

    # 🔁 Fallback (IMPORTANT)
    if not financial_docs:
        print("⚠️ No filtered docs → using raw docs")
        financial_docs = docs

    # 🔥 Step 3: Score + rank (VERY IMPORTANT)
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
        if "comprehensive income" in text:
            s -= 2  # avoid wrong section

        return s

    financial_docs = sorted(financial_docs, key=score, reverse=True)

    # 🔥 Step 4: Smart selection (TOP chunks only)
    sampled_docs = financial_docs[:12]

    partial_summaries = []

    # 🔥 Step 5: MAP
    for d in sampled_docs:
        chunk = d.page_content[:900]

        prompt = f"""
        Extract financial data ONLY.

        RULES:
        - Ignore risks, policies, generic text
        - Focus on:
            • revenue
            • net income
            • operating income
        - Capture ALL years if present
        - Do NOT guess or calculate

        If no financial data → return:
        NO DATA

        Text:
        {chunk}
        """

        try:
            response = llm.invoke(prompt)
            content = response.content if hasattr(response, "content") else str(response)

            if "NO DATA" not in content and len(content.strip()) > 30:
                partial_summaries.append(content)

        except Exception as e:
            print("⚠️ Error:", e)
            continue

    if not partial_summaries:
        return "No financial data could be extracted from the document.", []

    # 🔥 Step 6: REDUCE
    combined_text = "\n\n".join(partial_summaries[:10])

    final_prompt = f"""
    You are a senior financial analyst.

    STRICT RULES:
    - Use ONLY given data
    - Do NOT guess missing values
    - Do NOT repeat same trend
    - Keep output clean

    IMPORTANT:
    - Capture MULTI-YEAR data clearly
    - Prefer exact numbers
    - Keep formatting readable

    OUTPUT:

    Key Metrics:
    - Revenue (year-wise if available)
    - Net Income (year-wise if available)
    - Operating Income (year-wise if available)

    Financial Summary:
    - Bullet points (performance + trends)

    Simple Insights:
    - Is company growing?
    - Is profit strong?
    - Any major concern?

    Data:
    {combined_text}
    """

    final_response = llm.invoke(final_prompt)

    if hasattr(final_response, "content"):
        return final_response.content, sampled_docs

    else:
        return str(final_response), sampled_docs
