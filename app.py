import streamlit as st
import re
import math
from collections import Counter
import pandas as pd
import json

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM CSS
# ==========================================
st.set_page_config(
    page_title="LexiMetrics Pro | Text Analytics",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI enhancements
st.markdown("""
    <style>
    .stTextArea textarea {
        font-size: 16px !important;
        border-radius: 8px !important;
        border: 1px solid #d3d3d3;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CORE PROCESSING LOGIC (BACKEND ENGINE)
# ==========================================
def analyze_text(text: str, ignore_case: bool = True, exclude_stopwords: bool = False) -> dict:
    """
    Core engine to parse and analyze text with high accuracy using Regex.
    """
    if not text.strip():
        return None

    # Basic Counts
    char_count_total = len(text)
    char_count_no_spaces = len(text.replace(" ", "").replace("\n", ""))
    
    # Paragraphs (split by double newlines)
    paragraphs = [p for p in text.split('\n\n') if p.strip()]
    paragraph_count = len(paragraphs)
    
    # Sentences (split by punctuation marks . ! ?)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 0]
    sentence_count = len(sentences)
    
    # Words extraction using regex (handles punctuation correctly)
    if ignore_case:
        text_for_words = text.lower()
    else:
        text_for_words = text
        
    words = re.findall(r'\b\w+\b', text_for_words)
    word_count = len(words)
    
    # Optional: Stopword filtering for advanced analysis
    if exclude_stopwords:
        # A lightweight list of common English stopwords
        stopwords = {"the", "and", "a", "an", "is", "in", "it", "of", "to", "that", "this", "on", "for", "with", "as", "by", "at"}
        words = [w for w in words if w.lower() not in stopwords]

    # Advanced Metrics
    unique_words = set(words)
    unique_word_count = len(unique_words)
    
    # Lexical Density (Unique words / Total words)
    lexical_density = (unique_word_count / word_count * 100) if word_count > 0 else 0
    
    # Time Estimates (Average silent reading = 238 WPM, Speaking = 183 WPM)
    reading_time_mins = math.ceil(word_count / 238)
    speaking_time_mins = math.ceil(word_count / 183)

    # Word Frequency
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
# 3. FRONTEND UI & DASHBOARD
# ==========================================
def main():
    # Header Section
    st.title("📝 LexiMetrics Pro")
    st.markdown("**High-Fidelity Text Analysis & Word Counting Engine**")
    
    # Sidebar: Settings & Controls
    with st.sidebar:
        st.header("⚙️ Engine Settings")
        st.write("Adjust how the algorithm processes your text.")
        ignore_case = st.checkbox("Ignore Case Sensitivity", value=True, help="Treat 'Apple' and 'apple' as the same word.")
        exclude_stopwords = st.checkbox("Exclude Stop Words", value=False, help="Removes common words like 'the', 'and', 'is' from frequency analysis.")
        st.markdown("---")
        st.info("💡 **Pro Tip:** Paste your essay, article, or code documentation into the main area to instantly generate metrics.")

    # Main Input Area
    text_input = st.text_area(
        label="Enter your text below:", 
        height=300, 
        placeholder="Paste your document here to begin analysis..."
    )

    # Process Data Only if Text Exists
    if text_input.strip():
        with st.spinner("Analyzing text vectors..."):
            stats = analyze_text(text_input, ignore_case, exclude_stopwords)
        
        st.markdown("---")
        
        # TABBED INTERFACE FOR CLEAN DESIGN
        tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "📈 Frequency Analysis", "💾 Export Data"])
        
        # TAB 1: Dashboard Metrics
        with tab1:
            st.subheader("Core Metrics")
            
            # Using columns for a dashboard feel
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(label="Total Words", value=stats["word_count"])
            col2.metric(label="Characters (Total)", value=stats["char_count_total"])
            col3.metric(label="Characters (No Spaces)", value=stats["char_count_no_spaces"])
            col4.metric(label="Unique Words", value=stats["unique_word_count"])
            
            st.write("") # Spacer
            
            col5, col6, col7, col8 = st.columns(4)
            col5.metric(label="Sentences", value=stats["sentence_count"])
            col6.metric(label="Paragraphs", value=stats["paragraph_count"])
            col7.metric(label="Est. Reading Time", value=f"{stats['reading_time']} min")
            col8.metric(label="Est. Speaking Time", value=f"{stats['speaking_time']} min")

            # Progress bar for Lexical Density
            st.write("")
            st.markdown(f"**Lexical Density:** {stats['lexical_density']}% (Percentage of unique words)")
            st.progress(int(stats['lexical_density']))
            
        # TAB 2: Visualizations
        with tab2:
            st.subheader("Top 10 Most Frequent Words")
            if stats["word_freq"]:
                # Convert to Pandas DataFrame for native Streamlit charts
                df_freq = pd.DataFrame(stats["word_freq"], columns=["Word", "Frequency"])
                df_freq = df_freq.set_index("Word")
                
                # Render Bar Chart
                st.bar_chart(df_freq, use_container_width=True)
            else:
                st.warning("Not enough words to generate frequency charts.")

        # TAB 3: Data Export
        with tab3:
            st.subheader("Export Results")
            st.write("Download your text analytics for external reporting.")
            
            # Convert stats to JSON for download
            json_data = json.dumps(stats, indent=4)
            
            st.download_button(
                label="📥 Download Analytics Report (JSON)",
                data=json_data,
                file_name="leximetrics_report.json",
                mime="application/json"
            )
    else:
        st.info("Waiting for input. The dashboard will populate once you type or paste text above.")

if __name__ == "__main__":
    main()
