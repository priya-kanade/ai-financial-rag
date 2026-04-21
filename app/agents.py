from app.rag_pipeline import get_response
from app.map_reduce import map_reduce_summary   # ✅ NEW


def financial_agent(query, selected_file=None, mode_source="demo"):
    query_lower = query.lower()

    # 🔥 SUMMARY → Hybrid (MapReduce + RAG fallback)
    if "summary" in query_lower or "summarize" in query_lower:

        # ✅ Step 1: MapReduce returns (response, docs)
        response_text, docs = map_reduce_summary(selected_file, mode_source)

        # 🔥 Step 2: Check if response is weak
        weak_signals = [
            "not available",
            "no financial data",
            "not explicitly stated"
        ]

        if any(signal in response_text.lower() for signal in weak_signals):
            print("⚠️ MapReduce weak → falling back to RAG")

            # ✅ Step 3: fallback to RAG
            response_text, docs = get_response(
                "income statement revenue net income operating income financial results",
                selected_file,
                mode_source
            )
            return response_text, docs

        # ✅ Strong result → return MapReduce WITH sources
        return response_text, docs

    # 🔥 RISK → targeted RAG
    elif "risk" in query_lower:
        query = "risk factors uncertainties business risks financial risks"

    # 🔥 DEFAULT → normal RAG
    if isinstance(selected_file, list):
        if len(selected_file) > 1:
            return "⚠️ Please select ONLY ONE file for summary.", []
        selected_file = selected_file[0]
    response_text, docs = get_response(query, selected_file, mode_source)

    return response_text, docs