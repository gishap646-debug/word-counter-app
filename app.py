import streamlit as st
import re
import math
from collections import Counter
import pandas as pd
import json
import io

# ==========================================
# FAIL-SAFE DEPENDENCY MANAGER (MIT ENGINEERING STANDARD)
# ==========================================
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx
except ImportError:
    docx = None

try:
    from streamlit_mic_recorder import speech_to_text
except ImportError:
    speech_to_text = None

# ==========================================
# 1. PAGE CONFIGURATION & MODERN UI THEME
# ==========================================
st.set_page_config(
    page_title="LexiMetrics Ultra Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Glassmorphic CSS Styling for a premium analytics dashboard
st.markdown("""
    <style>
    /* Metric Card Styling */
    .metric-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        border: 1px solid #e2e8f0;
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
    }
    </style>
""", unsafe_allow_html=True)

# Initialize global asynchronous state engine
if "processed_text" not in st.session_state:
    st.session_state["processed_text"] = ""

# ==========================================
# 2. FILE EXTRACTION PIPELINE
# ==========================================
def extract_text_from_file(uploaded_file) -> str:
    """
    Parses Text, PDF, DOCX, and CSV streams safely into sanitized strings.
    """
    file_type = uploaded_file.name.split(".")[-1].lower()
    extracted_text = ""
    
    try:
        if file_type == "txt":
            extracted_text = uploaded_file.read().decode("utf-8", errors="ignore")
            
        elif file_type == "pdf":
            if PdfReader is not None:
                pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
                text_layers = [page.extract_text() for page in pdf_reader.pages if page.extract_text()]
                extracted_text = "\n".join(text_layers)
            else:
                st.error("❌ PDF Engine missing. Run: pip install pypdf")
                
        elif file_type in ["docx", "doc"]:
            if docx is not None:
                doc = docx.Document(io.BytesIO(uploaded_file.read()))
                extracted_text = "\n".join([para.text for para in doc.paragraphs])
            else:
                st.error("❌ Word Document Engine missing. Run: pip install python-docx")
                
        elif file_type == "csv":
            df = pd.read_csv(uploaded_file)
            extracted_text = df.to_string()
            
    except Exception as e:
        st.error(f"Data stream interpretation error: {str(e)}")
        
    return extracted_text

# ==========================================
# 3. ADVANCED ANALYTICS ENGINE
# ==========================================
def analyze_text(text: str, ignore_case: bool = True, exclude_stopwords: bool = False) -> dict:
    if not text.strip():
        return None

    char_count_total = len(text)
    char_count_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\r", ""))
    
    paragraphs = [p for p in text.split('\n') if p.strip()]
    paragraph_count = len(paragraphs)
    
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    sentence_count = max(len(sentences), 1 if char_count_total > 0 else 0)
    
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
# 4. USER INTERFACE RUNTIME
# ==========================================
def main():
    st.title("🧠 LexiMetrics Ultra Pro")
    st.markdown("### Next-Generation Computational Linguistics Console")
    st.markdown("---")
    
    # Sidebar Setup
    with st.sidebar:
        st.header("⚙️ Engine Parameters")
        ignore_case = st.checkbox("Ignore Case Sensitivity", value=True)
        exclude_stopwords = st.checkbox("Exclude Common Stop Words", value=False)
        
        st.markdown("---")
        st.header("🎙️ Voice Telemetry Input")
        
        if speech_to_text is not None:
            speech_text = speech_to_text(
                start_prompt="🔴 Click to Record Audio",
                stop_prompt="⏹️ Terminate Recording",
                language='en',
                use_container_width=True,
                key='speech_engine'
            )
            if speech_text:
                st.session_state["processed_text"] += " " + speech_text
                st.toast("Voice stream written to context memory!")
        else:
            st.warning("⚠️ Microphone engine offline. Run: `pip install streamlit-mic-recorder` to unlock.")

    # Multi-Channel Source Selection
    input_mode = st.radio("Select Content Source Layer:", ["⌨️ Workspace Text Buffer", "📂 File Ingestion Pipeline"], horizontal=True)

    if input_mode == "⌨️ Workspace Text Buffer":
        text_input = st.text_area(
            label="Live Data Stream Matrix:", 
            value=st.session_state["processed_text"],
            height=300, 
            placeholder="Type content, capture voice from sidebar, or review processed document streams here...",
            key="workspace_area"
        )
        st.session_state["processed_text"] = text_input
    else:
        uploaded_file = st.file_uploader("Target Node Ingest (TXT, PDF, DOCX, CSV)", type=["txt", "pdf", "docx", "csv"])
        if uploaded_file is not None:
            with st.spinner("Extracting multi-format structural layout..."):
                file_extracted = extract_text_from_file(uploaded_file)
                if file_extracted:
                    st.session_state["processed_text"] = file_extracted
        
        text_input = st.text_area(
            label="Extracted Context Preview (Editable):",
            value=st.session_state["processed_text"],
            height=200,
            key="file_preview_area"
        )
        st.session_state["processed_text"] = text_input

    # Analytics Matrix Execution
    if st.session_state["processed_text"].strip():
        stats = analyze_text(st.session_state["processed_text"], ignore_case, exclude_stopwords)
        
        if stats:
            st.markdown("---")
            tab1, tab2, tab3 = st.tabs(["📊 Metric Overview", "📈 Token Distribution", "💾 Export Schema"])
            
            with tab1:
                st.subheader("Core Quantitative Telemetry")
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.markdown(f'<div class="metric-card"><div class="metric-label">Total Words</div><div class="metric-value">{stats["word_count"]}</div></div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="metric-card"><div class="metric-label">Gross Characters</div><div class="metric-value">{stats["char_count_total"]}</div></div>', unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="metric-card"><div class="metric-label">Net Characters</div><div class="metric-value">{stats["char_count_no_spaces"]}</div></div>', unsafe_allow_html=True)
                with c4: st.markdown(f'<div class="metric-card"><div class="metric-label">Unique Tokens</div><div class="metric-value">{stats["unique_word_count"]}</div></div>', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                c5, c6, c7, c8 = st.columns(4)
                with c5: st.markdown(f'<div class="metric-card"><div class="metric-label">Sentences</div><div class="metric-value">{stats["sentence_count"]}</div></div>', unsafe_allow_html=True)
                with c6: st.markdown(f'<div class="metric-card"><div class="metric-label">Paragraph Blocks</div><div class="metric-value">{stats["paragraph_count"]}</div></div>', unsafe_allow_html=True)
                with c7: st.markdown(f'<div class="metric-card"><div class="metric-label">Reading Velocity</div><div class="metric-value">{stats["reading_time"]} min</div></div>', unsafe_allow_html=True)
                with c8: st.markdown(f'<div class="metric-card"><div class="metric-label">Speaking Velocity</div><div class="metric-value">{stats["speaking_time"]} min</div></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"**Lexical Density Coefficient:** `{stats['lexical_density']}%`")
                st.progress(int(stats['lexical_density']))
                
            with tab2:
                st.subheader("High-Frequency Token Density Distribution")
                if stats["word_freq"]:
                    df_freq = pd.DataFrame(stats["word_freq"], columns=["Token", "Count"]).set_index("Token")
                    st.bar_chart(df_freq, use_container_width=True, color="#3b82f6")
                else:
                    st.warning("Insufficient structural tokens to map distribution paths.")

            with tab3:
                st.subheader("Data Serialization Console")
                st.download_button(
                    label="📥 Export Report Array (JSON)",
                    data=json.dumps(stats, indent=4),
                    file_name="leximetrics_telemetry.json",
                    mime="application/json"
                )
    else:
        st.info("System standing by. Provide text via manual typing, document ingest, or voice telemetry to initialize calculations.")

if __name__ == "__main__":
    main()
