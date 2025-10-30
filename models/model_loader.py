"""
models/model_loader.py
โหลดและจัดการ ML Model
"""

import streamlit as st
from config import DEFAULT_MODEL_NAME
from utils.helpers import check_sentence_transformers_available

SENTENCE_TRANSFORMERS_AVAILABLE = check_sentence_transformers_available()

@st.cache_resource
def load_model(model_name: str = DEFAULT_MODEL_NAME):
    """โหลด Sentence Transformer model"""
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        st.warning("ไม่สามารถโหลด sentence-transformers ได้")
        return None
    
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(model_name)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None