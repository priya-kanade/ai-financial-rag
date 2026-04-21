import streamlit as st
import requests
import os

st.set_page_config(page_title="AI Financial Intelligence", layout="wide")

# -------------------------------
# 🔥 STYLED HEADER
# -------------------------------
st.markdown("""
<style>
.header {
    background: linear-gradient(90deg, #1e293b, #0f172a);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
}
.header h1 {
    color: #38bdf8;
    margin-bottom: 5px;
}
.header p {
    color: #94a3b8;
}
.card {
    background-color: #1e293b;
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 15px;
    border: 1px solid #334155;
}
.card h3 {
    color: #38bdf8;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <h1>📊 AI Financial Intelligence Platform</h1>
    <p>Analyze financial reports with structured AI insights</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# MODE SELECTION
# -------------------------------
mode = st.radio("Select Mode", ["Demo", "Upload"])

selected_file = None
uploaded_file_name = None

# -------------------------------
# DEMO MODE
# -------------------------------
if mode == "Demo":
    DATA_PATH = "data"
    files = [f for f in os.listdir(DATA_PATH) if f.endswith(".pdf")]
    selected_file = st.selectbox("📂 Select Report", files)

# -------------------------------
# -------------------------------
# UPLOAD MODE
# -------------------------------
st.sidebar.subheader("📤 Upload Your Own PDF")

# 🔥 INIT SESSION STORAGE
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    uploaded_file_name = uploaded_file.name

    # 🔥 Avoid duplicate uploads
    if uploaded_file_name not in st.session_state.uploaded_files:

        with st.sidebar.spinner("Uploading..."):
            res = requests.post(
                "http://127.0.0.1:8000/upload",
                files={"file": uploaded_file}
            )

            if res.status_code == 200:
                st.sidebar.success(f"✅ {uploaded_file_name} uploaded")

                # 🔥 STORE FILE NAME
                st.session_state.uploaded_files.append(uploaded_file_name)

            else:
                st.sidebar.error("Upload failed")
    else:
        st.sidebar.info(f"{uploaded_file_name} already uploaded")

# -------------------------------
# 🔥 MULTI FILE SELECT (NEW)
# -------------------------------
st.sidebar.markdown("### 📂 Select Uploaded Reports")

selected_uploads = st.sidebar.multiselect(
    "Choose files",
    st.session_state.uploaded_files
)

# -------------------------------
# 🔥 SHOW ACTIVE UPLOADS
# -------------------------------
if selected_uploads:
    st.sidebar.success(f"Using: {', '.join(selected_uploads)}")
# -------------------------------
# ACTIVE DOCUMENT
# -------------------------------
st.markdown("### 📄 Active Document")

if mode == "Upload" and uploaded_file_name:
    st.success(f"Using uploaded file: {uploaded_file_name}")
elif mode == "Demo" and selected_file:
    st.info(f"Using demo file: {selected_file}")
else:
    st.warning("No document selected")

# -------------------------------
# ACTION BUTTONS
# -------------------------------
st.markdown("### ⚡ Actions")

col1, col2 = st.columns(2)

query = ""

with col1:
    if st.button("📊 Summarize Report"):
        query = "summary"

with col2:
    if st.button("⚠️ Find Risks"):
        query = "risk"

# -------------------------------
# CUSTOM QUERY
# -------------------------------
user_query = st.text_input("💬 Ask your own question")

if user_query:
    query = user_query

# -------------------------------
# API CALL
# -------------------------------
if query:
    with st.spinner("Analyzing..."):

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
            st.error("API Error")
        else:
            data = res.json()
            response = data["response"]

            st.markdown("## 📊 Results")

            # -------------------------------
            # 🔥 SPLIT INTO SECTIONS
            # -------------------------------
            sections = {
                "📊 Key Metrics": "",
                "📈 Financial Summary": "",
                "⚠️ Key Risks": "",
                 "✅ Positive Signals": "",
                "💡 Insights": ""
            }

            current_section = None

            for line in response.split("\n"):
                l = line.strip().lower()

                if "key metrics" in l:
                    current_section = "📊 Key Metrics"
                elif "financial summary" in l or "financial health" in l:
                    current_section = "📈 Financial Summary"
                elif "key risks" in l:
                    current_section = "⚠️ Key Risks"
                elif "positive signals" in l or "strengths" in l:
                    current_section = "✅ Positive Signals"
                elif "insight" in l:
                    current_section = "💡 Insights"

                if current_section:
                    sections[current_section] += line + "\n"

            # -------------------------------
            # 🔥 CARD DISPLAY
            # -------------------------------
            for title, content in sections.items():
                if content.strip():
                    st.markdown(f"""
                    <div class="card">
                        <h3>{title}</h3>
                        <pre style="white-space: pre-wrap; color:white;">{content}</pre>
                    </div>
                    """, unsafe_allow_html=True)

            # -------------------------------
            # SOURCES
            # -------------------------------
            st.markdown("## 📄 Sources")

            for i, s in enumerate(data["sources"], 1):
                with st.expander(f"Source {i} — Page {s['page']}"):
                    st.write(f"📁 {s['file']}")
                    st.write(s["snippet"])