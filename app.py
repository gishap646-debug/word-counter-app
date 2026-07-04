import streamlit as st
import re
import math
from collections import Counter
import pandas as pd
import json
import io

# Advanced File Parsers
from pypdf import PdfReader
try:
    import docx
except ImportError:
    docx = None

# Audio Processing Component
from streamlit_mic_recorder import speech_to_text

# ==========================================
# 1. ENHANCED PAGE CONFIGURATION & UI ARCHITECTURE
# ==========================================
st.set_page_config(
    page_title="LexiMetrics Ultra Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Glassmorphic CSS Styling for an ultra-modern dashboard experience
st.markdown("""
    <style>
    /* Main container enhancements */
    .reportview-container {
        background: #fdfdfd;
    }
    /* Metric Card Styling */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #eef2f6;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.8rem;
        color: #0f172a;
        font-weight: 700;
        margin-top: 4px;
    }
    /* Textarea optimization */
    .stTextArea textarea {
        font-size: 16px !important;
        border-radius: 10px !important;
        border: 1px solid #cbd5e1 !important;
        transition: border-color 0.2s ease;
    }
    .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Streamlit Session State for asynchronous text synchronization
if "processed_text" not in st.session_state:
    st.session_state["processed_text"] = ""

# ==========================================
# 2. FILE EXTRACTION ENGINE (BACKEND PIPELINE)
# ==========================================
def extract_text_from_file(uploaded_file) -> str:
    """
    Safely reads and parses Text, PDF, and DOCX byte streams into sanitized strings.
    """
    file_type = uploaded_file.name.split(".")[-1].lower()
    extracted_text = ""
    
    try:
        if file_type == "txt":
            extracted_text = uploaded_file.read().decode("utf-8", errors="ignore")
            
        elif file_type == "pdf":
            pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
            text_layers = []
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_layers.append(page_text)
            extracted_text = "\n".join(text_layers)
            
        elif file_type in ["docx", "doc"]:
            if docx is not None:
                doc = docx.Document(io.BytesIO(uploaded_file.read()))
                extracted_text = "\n".join([para.text for para in doc.paragraphs])
            else:
                st.error("Engine failure: 'python-docx' library is not configured on the server host.")
                
        elif file_type == "csv":
            df = pd.read_csv(uploaded_file)
            extracted_text = df.to_string()
            
    except Exception as e:
        st.error(f"Data corruption event during structural analysis: {str(e)}")
        
    return extracted_text

# ==========================================
# 3. CORE PROCESSING LOGIC (ANALYTICS ENGINE)
# ==========================================
def analyze_text(text: str, ignore_case: bool = True, exclude_stopwords: bool = False) -> dict:
    """
    Mathematical parsing framework using optimized Regular Expressions for high precision tokenization.
    """
    if not text.strip():
        return None

    char_count_total = len(text)
    char_count_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\r", ""))
    
    # Paragraph tokenization via carriage-return isolation
    paragraphs = [p for p in text.split('\n') if p.strip()]
    paragraph_count = len(paragraphs)
    
    # Sentence tokenization via advanced punctuation boundaries
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 0]
    sentence_count = max(len(sentences), 1 if char_count_total > 0 else 0)
    
    # Tokenizing lexical sets
    text_for_words = text.lower() if ignore_case else text
    words = re.findall(r'\b\w+\b', text_for_words)
    word_count = len(words)
    
    if exclude_stopwords:
        stopwords = {"the", "and", "a", "an", "is", "in", "it", "of", "to", "that", "this", "on", "for", "with", "as", "by", "at", "from"}
        words = [w for w in words if w.lower() not in stopwords]

    unique_words = set(words)
    unique_word_count = len(unique_words)
    
    lexical_density = (unique_word_count / word_count * 100) if word_count > 0 else 0
    lexical_density = min(lexical_density, 100.0)
    
    # MIT Scientific standard operational constants for read/speak velocities
    reading_time_mins = max(1, math.ceil(word_count / 238)) if word_count > 0 else 0
    speaking_time_mins = max(1, math.ceil(word_count / 183)) if word_count > 0 else 0

    word_freq = Counter(words).most_common(10)

    return {
        "word_count": word_count,
        "char_count_total": char_count_total,
        "char_count_no_spaces": char_count_no_spaces,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "unique_word_count": unique_word_count,
        "lexical_density": round(lexical_density, 2),
        "reading_time": reading_time_mins,
        "speaking_time": speaking_time_mins,
        "word_freq": word_freq
    }

# ==========================================
# 4. FRONTEND UI & INTERACTIVE DASHBOARD
# ==========================================
def main():
    # Structural Title Block
    st.title("🧠 LexiMetrics Ultra Pro")
    st.markdown("### Next-Generation Computational Linguistics & Telemetry Console")
    st.markdown("---")
    
    # Sidebar: Core Configuration Engines
    with st.sidebar:
        st.header("⚙️ Engine Control Unit")
        ignore_case = st.checkbox("Ignore Case Sensitivity", value=True, help="Normalizes token mapping to neutralize casing variance.")
        exclude_stopwords = st.checkbox("Exclude English Stop Words", value=False, help="Filters foundational structural syntax from frequency distribution profiles.")
        
        st.markdown("---")
        st.header("🎙️ Omnidirectional Voice Capture")
        st.write("Convert raw voice recordings directly into the text editor system matrix in real-time.")
        
        # Real-time microphone to text engine block
        speech_text = speech_to_text(
            start_prompt="🔴 Click to Record Audio",
            stop_prompt="⏹️ Terminate Recording",
            language='en',
            use_container_width=True,
            key='speech_engine'
        )
        
        if speech_text:
            st.session_state["processed_text"] += " " + speech_text
            st.success("Audio byte successfully processed and injected below!")

    # Multi-Source Input Splitter
    input_mode = st.radio("Select Content Sourcing Core:", ["⌨️ Manual Input / Buffer Append", "📂 Unified Document File Upload Engine"], horizontal=True)

    if input_mode == "⌨️ Manual Input / Buffer Append":
        # Interactive Workspace
        text_input = st.text_area(
            label="Workspace Buffer Input Matrix:", 
            value=st.session_state["processed_text"],
            height=320, 
            placeholder="Type manually, record audio from the sidebar, or append metrics data streams here...",
            key="workspace_area"
        )
        # Keep internal session state cleanly updated dynamically
        st.session_state["processed_text"] = text_input
    
    else:
        # File ingest array pipeline
        uploaded_file = st.file_uploader(
            "Target Ingest Node (Supports: .TXT, .PDF, .DOCX, .CSV)", 
            type=["txt", "pdf", "docx", "csv"],
            help="Direct stream processing interface for document structures."
        )
        
        if uploaded_file is not None:
            with st.spinner("Executing extraction sequences across documents..."):
                file_extracted = extract_text_from_file(uploaded_file)
                if file_extracted:
                    st.session_state["processed_text"] = file_extracted
                    st.success(f"Successfully processed {uploaded_file.name} into analytics engine memory!")
        
        # Display editable preview matrix of the parsed data stream
        text_input = st.text_area(
            label="Parsed Text Buffer Preview Container (Editable):",
            value=st.session_state["processed_text"],
            height=200,
            key="file_preview_area"
        )
        st.session_state["processed_text"] = text_input

    # Execution Processing Gate
    if st.session_state["processed_text"].strip():
        with st.spinner("Analyzing operational text arrays..."):
            stats = analyze_text(st.session_state["processed_text"], ignore_case, exclude_stopwords)
        
        if stats:
            st.markdown("---")
            
            # Tab Layout Controller
            tab1, tab2, tab3 = st.tabs(["📊 Executive Overview Dashboard", "📈 Computational Frequency Charts", "💾 Data Export Core"])
            
            # TAB 1: Advanced Metric Distribution Cards
            with tab1:
                st.subheader("Core Quantitative Metrics")
                
                # Rows implemented via neat metric columns
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Total Word Matrix</div><div class="metric-value">{stats["word_count"]}</div></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Characters (Gross)</div><div class="metric-value">{stats["char_count_total"]}</div></div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Characters (Net)</div><div class="metric-value">{stats["char_count_no_spaces"]}</div></div>', unsafe_allow_html=True)
                with c4:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Unique Vocabulary</div><div class="metric-value">{stats["unique_word_count"]}</div></div>', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                c5, c6, c7, c8 = st.columns(4)
                with c5:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Sentence Nodes</div><div class="metric-value">{stats["sentence_count"]}</div></div>', unsafe_allow_html=True)
                with c6:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Paragraph Blocks</div><div class="metric-value">{stats["paragraph_count"]}</div></div>', unsafe_allow_html=True)
                with c7:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Est. Silent Reading</div><div class="metric-value">{stats["reading_time"]} min</div></div>', unsafe_allow_html=True)
                with c8:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Est. Oral Speaking</div><div class="metric-value">{stats["speaking_time"]} min</div></div>', unsafe_allow_html=True)

                # Density Distribution Meter Array
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"**Lexical Density Spectrum Index:** `{stats['lexical_density']}%` (Proportional usage weight of unique vocabulary structures)")
                st.progress(int(stats['lexical_density']))
                
            # TAB 2: Visualizations Analytics Hub
            with tab2:
                st.subheader("Frequency Density Optimization Chart")
                if stats["word_freq"]:
                    df_freq = pd.DataFrame(stats["word_freq"], columns=["Token", "Density Score"]).set_index("Token")
                    st.bar_chart(df_freq, use_container_width=True, color="#3b82f6")
                else:
                    st.warning("Data payload density contains insufficient words to render token maps.")

            # TAB 3: Advanced Data Export Matrix
            with tab3:
                st.subheader("Export Architecture Target Configuration")
                st.write("Serialize and transmit metrics calculations via JSON format arrays.")
                
                json_data = json.dumps(stats, indent=4)
                st.download_button(
                    label="📥 Export System Telemetry Metrics (JSON)",
                    data=json_data,
                    file_name="leximetrics_ultra_telemetry.json",
                    mime="application/json"
                )
    else:
        st.info("System is currently sitting idle. Please populate data strings via manual inputs, document uploads, or real-time voice telemetry to initialize analysis pipelines.")

if __name__ == "__main__":
    main()
