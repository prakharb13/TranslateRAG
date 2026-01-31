import streamlit as st
import httpx
import os

# Read backend URL from environment variable (for Docker)
# Defaults to localhost for local development
API_BASE = os.getenv("BACKEND_URL", "http://localhost:8000/api")

st.set_page_config(page_title="TranslateRAG", layout="wide")
st.title("TranslateRAG")


@st.cache_data(ttl=60)
def get_languages():
    try:
        r = httpx.get(f"{API_BASE}/languages", timeout=5)
        return r.json()["languages"]
    except Exception:
        return ["English", "French", "German", "Spanish", "Hindi", "Chinese (Simplified)",
                "Japanese", "Korean", "Arabic", "Russian", "Portuguese", "Italian"]


languages = get_languages()

tab_translate, tab_ask, tab_docs = st.tabs(["Translate Document", "Translate / Ask", "Manage Documents"])

# --- Translate Document Tab ---
with tab_translate:
    st.subheader("Translate an entire document")

    col1, col2 = st.columns(2)
    with col1:
        doc_source_lang = st.selectbox("Source language", languages,
                                       index=languages.index("English") if "English" in languages else 0,
                                       key="doc_src")
    with col2:
        doc_target_lang = st.selectbox("Target language", languages,
                                       index=languages.index("French") if "French" in languages else 1,
                                       key="doc_tgt")

    doc_file = st.file_uploader("Upload a document (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"], key="doc_translate")

    if doc_file and st.button("Translate Document", type="primary"):
        with st.spinner("Translating document..."):
            try:
                r = httpx.post(
                    f"{API_BASE}/translate-document",
                    files={"file": (doc_file.name, doc_file.getvalue(), doc_file.type)},
                    data={"source_language": doc_source_lang, "target_language": doc_target_lang},
                    timeout=600,
                )
                r.raise_for_status()
                data = r.json()
                st.text_area("Translation", value=data["full_translation"], height=400, disabled=True)
                st.download_button(
                    "Download translation as TXT",
                    data=data["full_translation"],
                    file_name=f"translated_{doc_file.name.rsplit('.', 1)[0]}.txt",
                    mime="text/plain",
                )
            except httpx.HTTPStatusError as e:
                st.error(f"API error: {e.response.text}")
            except Exception as e:
                st.error(f"Error: {e}")

# --- Ask Questions Tab ---
with tab_ask:
    st.subheader("Translate text or ask questions about documents")

    mode = st.radio("Mode", ["Translate", "Ask Question (RAG)"], horizontal=True, key="ask_mode")

    col1, col2 = st.columns(2)
    with col1:
        ask_source_lang = st.selectbox("Source language", languages,
                                       index=languages.index("English") if "English" in languages else 0,
                                       key="ask_src")
    with col2:
        ask_target_lang = st.selectbox("Target language", languages,
                                       index=languages.index("French") if "French" in languages else 1,
                                       key="ask_tgt")

    if mode == "Translate":
        question = st.text_area("Text to translate", height=150, key="ask_input")
    else:
        question = st.text_area("Question about indexed documents", height=150, key="ask_input")

    if st.button("Submit", type="primary", disabled=not question.strip()):
        with st.spinner("Processing..."):
            try:
                use_rag = mode == "Ask Question (RAG)"
                r = httpx.post(
                    f"{API_BASE}/ask",
                    json={
                        "question": question,
                        "source_language": ask_source_lang,
                        "target_language": ask_target_lang,
                        "use_rag": use_rag,
                    },
                    timeout=600,
                )
                r.raise_for_status()
                data = r.json()
                if data.get("mode") == "translation":
                    st.markdown("**Translation:**")
                else:
                    st.markdown("**Answer** (using RAG from indexed documents):")
                st.text_area("Result", value=data["answer"], height=200, disabled=True)
                if data["context_snippets"]:
                    with st.expander("Retrieved context from documents"):
                        for i, snippet in enumerate(data["context_snippets"], 1):
                            st.markdown(f"**Chunk {i}:**")
                            st.code(snippet, language=None)
            except httpx.HTTPStatusError as e:
                st.error(f"API error: {e.response.text}")
            except Exception as e:
                st.error(f"Error: {e}")

# --- Manage Documents Tab ---
with tab_docs:
    st.subheader("Index documents for RAG")
    st.caption("Upload documents here so the 'Ask Questions' tab can search them for answers.")

    uploaded = st.file_uploader("Upload a document (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"], key="doc_index")
    if uploaded and st.button("Index document"):
        with st.spinner("Uploading and indexing..."):
            try:
                r = httpx.post(
                    f"{API_BASE}/documents/upload",
                    files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type)},
                    timeout=600,
                )
                r.raise_for_status()
                info = r.json()
                st.success(f"Indexed **{info['filename']}** ({info['chunk_count']} chunks)")
            except httpx.HTTPStatusError as e:
                st.error(f"Upload error: {e.response.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

    st.subheader("Indexed Documents")
    try:
        r = httpx.get(f"{API_BASE}/documents", timeout=5)
        r.raise_for_status()
        docs = r.json()
        if not docs:
            st.info("No documents indexed yet.")
        for doc in docs:
            col_name, col_chunks, col_del = st.columns([3, 1, 1])
            col_name.write(doc["filename"])
            col_chunks.write(f"{doc['chunk_count']} chunks")
            if col_del.button("Delete", key=doc["id"]):
                httpx.delete(f"{API_BASE}/documents/{doc['id']}", timeout=10)
                st.rerun()
    except Exception:
        st.warning("Could not connect to backend. Is the API running?")
