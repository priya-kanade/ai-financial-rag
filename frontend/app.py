import streamlit as st
import requests
import os
import json

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="AI Financial Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS
# =====================================================
st.markdown("""
<style>

/* =========================
   GLOBAL
========================= */

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main {
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.12), transparent 25%),
        radial-gradient(circle at bottom right, rgba(56,189,248,0.08), transparent 25%),
        #0f172a;
    color: white;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* =========================
   HERO SECTION
========================= */

.hero {
    background: linear-gradient(
        135deg,
        rgba(17,24,39,0.92),
        rgba(30,41,59,0.88)
    );

    backdrop-filter: blur(18px);

    padding: 36px;
    border-radius: 26px;

    border: 1px solid rgba(255,255,255,0.08);

    margin-bottom: 28px;

    box-shadow:
        0 0 60px rgba(56,189,248,0.08),
        0 10px 30px rgba(0,0,0,0.35);
}

.hero-title {
    font-size: 42px;
    font-weight: 700;
    color: white;
    margin-bottom: 10px;
    letter-spacing: -0.5px;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 16px;
    line-height: 1.6;
}

/* =========================
   CARDS
========================= */

.metric-card,
.result-card,
.chat-user,
.chat-ai {

    background: rgba(17,24,39,0.78);

    backdrop-filter: blur(14px);

    border-radius: 22px;

    border: 1px solid rgba(255,255,255,0.06);

    transition: all 0.28s ease;

    box-shadow:
        0 8px 20px rgba(0,0,0,0.25);

}

/* Hover effect */

.metric-card:hover,
.result-card:hover,
.chat-user:hover,
.chat-ai:hover {

    transform: translateY(-4px);

    border-color: rgba(56,189,248,0.22);

    box-shadow:
        0 14px 35px rgba(56,189,248,0.08),
        0 8px 25px rgba(0,0,0,0.35);
}

/* =========================
   METRIC CARDS
========================= */

.metric-card {
    padding: 22px;
    margin-bottom: 16px;
}

.metric-title {
    color: #94a3b8;
    font-size: 14px;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-value {
    font-size: 24px;
    font-weight: 700;
    color: white;
}

/* =========================
   RESULT SECTION
========================= */

.result-card {
    padding: 26px;
    margin-top: 20px;
}

.result-card h3 {
    color: #38bdf8;
}

/* =========================
   CHAT UI
========================= */

.chat-user {
    padding: 16px;
    margin-bottom: 12px;

    background: rgba(30,41,59,0.78);
}

.chat-ai {
    padding: 20px;
    margin-bottom: 20px;

    border: 1px solid rgba(56,189,248,0.18);
}

/* =========================
   BUTTONS
========================= */

.stButton > button {

    width: 100%;

    height: 52px;

    border-radius: 14px;

    border: none;

    background:
        linear-gradient(
            90deg,
            #0ea5e9,
            #2563eb
        );

    color: white;

    font-weight: 600;

    font-size: 15px;

    transition: all 0.25s ease;

    box-shadow:
        0 8px 20px rgba(37,99,235,0.25);
}

.stButton > button:hover {

    transform: translateY(-2px);

    box-shadow:
        0 12px 28px rgba(37,99,235,0.38);

    filter: brightness(1.05);
}

/* =========================
   INPUTS
========================= */

.stTextInput input {

    background: rgba(17,24,39,0.82) !important;

    border: 1px solid rgba(255,255,255,0.08) !important;

    border-radius: 14px !important;

    color: white !important;

    height: 50px;
}

/* =========================
   SIDEBAR
========================= */

[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            #111827,
            #0f172a
        );

    border-right:
        1px solid rgba(255,255,255,0.06);
}

/* =========================
   DOWNLOAD BUTTON
========================= */

.stDownloadButton > button {

    border-radius: 12px;

    border: 1px solid rgba(56,189,248,0.15);

    background: rgba(17,24,39,0.85);

    color: white;

    transition: all 0.25s ease;
}

.stDownloadButton > button:hover {

    border-color: rgba(56,189,248,0.3);

    transform: translateY(-2px);
}

/* =========================
   FOOTER
========================= */

.footer {

    margin-top: 80px;

    padding-top: 30px;

    padding-bottom: 25px;

    border-top: 1px solid rgba(255,255,255,0.08);

    text-align: center;

    background: rgba(255,255,255,0.01);

    border-radius: 20px;

    backdrop-filter: blur(10px);

    line-height: 1.8;
}

/* =========================
   SCROLLBAR
========================= */

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: #0f172a;
}

::-webkit-scrollbar-thumb {
    background: rgba(56,189,248,0.25);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(56,189,248,0.45);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown("## 📊 AI Financial Intelligence")
    st.caption("Enterprise Financial Report Analysis")

    st.markdown("---")

    mode = st.radio(
        "Workspace Mode",
        ["Demo", "Upload"]
    )

    # SESSION STORAGE
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    st.markdown("---")

    st.subheader("📤 Upload Reports")

    uploaded_file = st.file_uploader(
        "Upload Financial PDF",
        type=["pdf"]
    )

    if uploaded_file:
        uploaded_file_name = uploaded_file.name

        if uploaded_file_name not in st.session_state.uploaded_files:

            with st.spinner("Uploading and indexing document..."):
                res = requests.post(
                    "http://127.0.0.1:8000/upload",
                    files={"file": uploaded_file}
                )

                if res.status_code == 200:
                    st.success(f"✅ {uploaded_file_name} uploaded")
                    st.session_state.uploaded_files.append(uploaded_file_name)
                else:
                    st.error("Upload failed")

    st.markdown("---")

    st.subheader("📂 Uploaded Reports")

    selected_uploads = st.multiselect(
        "Select uploaded reports",
        st.session_state.uploaded_files
    )

# =====================================================
# HERO SECTION
# =====================================================
st.markdown("""
<div class="hero">
    <div class="hero-title">📊 AI Financial Intelligence Platform</div>
    <div class="hero-subtitle">
        Analyze annual reports using Retrieval-Augmented Generation, financial extraction, and AI-driven insights.
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# DOCUMENT SELECTION
# =====================================================
selected_file = None

if mode == "Demo":
    DATA_PATH = "data"
    files = [f for f in os.listdir(DATA_PATH) if f.endswith(".pdf")]

    selected_file = st.selectbox(
        "📄 Select Financial Report",
        files
    )

# =====================================================
# STATUS CARDS
# =====================================================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Workspace Mode</div>
        <div class="metric-value">{mode}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    active_doc = selected_file if mode == "Demo" else (
        selected_uploads[0] if selected_uploads else "None"
    )

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Active Document</div>
        <div class="metric-value" style="font-size:18px;">{active_doc}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">AI Features</div>
        <div class="metric-value" style="font-size:18px;">RAG + MapReduce</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# ACTIONS
# =====================================================
st.markdown("## ⚡ Financial Analysis")

col1, col2 = st.columns(2)

query = ""

with col1:
    if st.button("📊 Generate Financial Summary"):
        query = "summary"

with col2:
    if st.button("⚠️ Analyze Business Risks"):
        query = "risk"

# =====================================================
# ANALYSIS
# =====================================================
if query:

    with st.spinner("📊 Analyzing financial report..."):

        payload = {
            "query": query,
            "mode_source": "upload" if mode == "Upload" else "demo"
        }

        if mode == "Demo":
            payload["selected_file"] = selected_file
        else:
            payload["selected_file"] = selected_uploads if selected_uploads else None

        res = requests.post(
            "http://127.0.0.1:8000/analyze",
            json=payload
        )

        if res.status_code != 200:
            st.error("⚠️ Error analyzing report")

        else:
            data = res.json()
            response = data["response"]

            safe_response = response.replace("<", "&lt;").replace(">", "&gt;")

            st.markdown(
                f"""
                <div class="result-card">

                    <h3 style="color:#38bdf8;">
                        📈 Analysis Results
                    </h3>

                    <div style="
                        color:white;
                        line-height:1.8;
                        font-size:15px;
                        white-space:pre-wrap;
                    ">
                        {safe_response}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            

            # DOWNLOAD
            st.download_button(
                label="📥 Download Analysis",
                data=response,
                file_name="financial_analysis.txt",
                mime="text/plain"
            )

# =====================================================
# CHATBOT
# =====================================================
st.markdown("## 💬 Chat with Financial Report")

chat_query = st.text_input(
    "Ask anything about the financial report",
    placeholder="Example: What is the total revenue?"
)

if st.button("Ask AI"):

    if not chat_query:
        st.warning("Please enter a question")

    else:

        with st.spinner("🤖 Generating AI response..."):

            payload = {
                "query": chat_query,
                "mode_source": "upload" if mode == "Upload" else "demo",
                "selected_file": selected_file if mode == "Demo" else (
                    selected_uploads[0] if selected_uploads else None
                )
            }

            res = requests.post(
                "http://127.0.0.1:8000/chat",
                params=payload
            )

            if res.status_code != 200:
                st.error("⚠️ Chat analysis failed")

            else:
                answer = res.json()["answer"]

                st.markdown(f"""
                <div class="chat-user">
                    <b>👤 You</b><br>
                    {chat_query}
                </div>
                """, unsafe_allow_html=True)

                safe_answer = answer.replace("<", "&lt;").replace(">", "&gt;")

                st.markdown(
                    f"""
                    <div class="chat-ai">

                        <h3 style="color:#38bdf8;">
                            🤖 AI Financial Assistant
                        </h3>

                        <div style="
                            color:white;
                            line-height:1.8;
                            font-size:15px;
                            white-space:pre-wrap;
                        ">
                            {safe_answer}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

# =====================================================
# FOOTER
# =====================================================
st.markdown('<div class="footer" style="margin-top: 80px; padding-top: 30px; padding-bottom: 25px; border-top: 1px solid rgba(255,255,255,0.08); text-align: center; background: rgba(255,255,255,0.01); border-radius: 20px; backdrop-filter: blur(10px); line-height: 1.8;"><div style="font-size:22px; font-weight:700; color:white; margin-bottom:8px; letter-spacing:-0.3px;">📊 AI Financial Intelligence Platform</div><div style="color:#94a3b8; font-size:15px; margin-bottom:20px;">Enterprise-grade financial analysis powered by AI, RAG, and intelligent document retrieval</div><div style="margin-bottom:20px;"><span style="background:rgba(56,189,248,0.12); color:#38bdf8; padding:7px 14px; border-radius:999px; font-size:13px; margin-right:8px; border:1px solid rgba(56,189,248,0.18); display:inline-block;">RAG</span><span style="background:rgba(37,99,235,0.12); color:#60a5fa; padding:7px 14px; border-radius:999px; font-size:13px; margin-right:8px; border:1px solid rgba(37,99,235,0.18); display:inline-block;">FastAPI</span><span style="background:rgba(16,185,129,0.12); color:#34d399; padding:7px 14px; border-radius:999px; font-size:13px; margin-right:8px; border:1px solid rgba(16,185,129,0.18); display:inline-block;">FAISS</span><span style="background:rgba(168,85,247,0.12); color:#c084fc; padding:7px 14px; border-radius:999px; font-size:13px; border:1px solid rgba(168,85,247,0.18); display:inline-block;">LLaMA 3</span></div><div style="color:#64748b; font-size:13px;">Designed & Developed by <span style="color:white; font-weight:600;">Priya Kanade</span></div></div>', unsafe_allow_html=True)