import streamlit as st
import os
import html
from core.document_loader import DocumentProcessor
from core.vector_store import VectorStore
from core.rag_chain import RAGEngine

# Page Configuration
st.set_page_config(
    page_title="DocuMind AI | RAG Document Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for modern UI & Footer
st.markdown("""
<style>
    .stApp {
        background-color: #0a0a0f;
        color: #ffffff;
    }
    .css-1d3780e, .stSidebar {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stButton>button {
        background: linear-gradient(45deg, #8a2be2, #00d2ff);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 8px 24px;
        font-weight: 600;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
    }
    footer {
        text-align: center;
        padding: 20px;
        color: #a0a0b0;
        font-size: 0.85rem;
        border-top: 1px solid rgba(255,255,255,0.08);
        margin-top: 50px;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStore()
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = RAGEngine(st.session_state.vector_store)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "processed_files" not in st.session_state:
    st.session_state.processed_files = []

# Header
st.title("🧠 DocuMind AI")
st.caption("Retrieval-Augmented Generation (RAG) Platform with Vector Database & Source Attribution")

# Sidebar
with st.sidebar:
    st.header("📄 Document Ingestion")
    
    chunk_size = st.slider("Chunk Size (characters)", 200, 1000, 500, step=100)
    chunk_overlap = st.slider("Chunk Overlap (characters)", 0, 200, 50, step=25)
    
    uploaded_files = st.file_uploader(
        "Upload PDF or TXT documents (Max 20MB)",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True
    )
    
    if st.button("⚡ Index Documents into Vector DB"):
        if uploaded_files:
            processor = DocumentProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            total_chunks = 0
            
            for file in uploaded_files:
                if file.name not in st.session_state.processed_files:
                    try:
                        chunks = processor.process_file(file)
                        st.session_state.vector_store.add_chunks(chunks)
                        st.session_state.processed_files.append(file.name)
                        total_chunks += len(chunks)
                    except Exception as e:
                        st.error(f"Error processing {file.name}: {str(e)}")
                    
            if total_chunks > 0:
                st.success(f"Successfully indexed document(s) into {total_chunks} vector chunks!")
        else:
            st.warning("Please upload at least one document.")
            
    st.divider()
    
    # Pre-built Sample Document Loader for Quick Testing
    st.subheader("🧪 Quick Test")
    if st.button("📄 Load Pre-Built Sample AI Paper"):
        sample_path = os.path.join("sample_docs", "AI_Architecture_Overview.txt")
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                class DummyFile:
                    name = "AI_Architecture_Overview.txt"
                    def read(self): return f.read()
                    def seek(self, pos, whence=0): return f.seek(pos, whence)
                    def tell(self): return f.tell()
                
                processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
                dummy = DummyFile()
                chunks = processor.process_file(dummy)
                st.session_state.vector_store.add_chunks(chunks)
                if dummy.name not in st.session_state.processed_files:
                    st.session_state.processed_files.append(dummy.name)
                st.success("Sample AI Architecture document loaded & indexed!")
                
    st.divider()
    st.subheader("📊 Vector DB Metrics")
    st.metric("Total Indexed Chunks", len(st.session_state.vector_store.chunks))
    st.metric("Active Documents", len(st.session_state.processed_files))
    
    if st.button("🗑️ Clear Vector Database"):
        st.session_state.vector_store.clear()
        st.session_state.processed_files = []
        st.session_state.chat_history = []
        st.rerun()

# Main Chat Interface
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Query Documents")
    
    user_query = st.text_input(
        "Ask any question based on your uploaded documents:",
        placeholder="e.g., What are the security and governance standards?"
    )
    
    if st.button("Ask DocuMind AI") and user_query:
        sanitized_query = html.escape(user_query.strip())
        with st.spinner("Searching vector database & synthesizing answer..."):
            result = st.session_state.rag_engine.query(sanitized_query)
            
            st.session_state.chat_history.append({
                "question": sanitized_query,
                "answer": result["answer"],
                "sources": result["sources"]
            })
            
    # Display Chat Trajectory
    for q_idx, item in enumerate(reversed(st.session_state.chat_history)):
        with st.container():
            st.markdown(f"**❓ Question:** {item['question']}")
            st.markdown(item["answer"])
            
            if item["sources"]:
                with st.expander("📌 View Attributed Sources & Pages"):
                    for s in item["sources"]:
                        st.markdown(f"- **Document:** `{s['filename']}` | **Page:** `{s['page']}`")
                        st.caption(f"Snippet: \"{s['snippet']}\"")
            st.divider()

with col2:
    st.subheader("📁 Indexed Documents")
    if st.session_state.processed_files:
        for fname in st.session_state.processed_files:
            st.markdown(f"✅ `{fname}`")
    else:
        st.info("No documents uploaded yet. Click '📄 Load Pre-Built Sample AI Paper' in the sidebar for quick testing!")

# Footer
st.markdown("""
<footer>
    © 2026 Ricardo Ratovoarisoa. All rights reserved. Built with passion & Enterprise Standards.
</footer>
""", unsafe_allow_html=True)
