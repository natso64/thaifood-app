"""
models/embeddings.py
สร้างและจัดการ Embeddings
"""

import os
import pickle
import numpy as np
import streamlit as st
from config import EMBEDDINGS_NAME_PATH, EMBEDDINGS_INGREDIENT_PATH
from utils.helpers import check_sentence_transformers_available

SENTENCE_TRANSFORMERS_AVAILABLE = check_sentence_transformers_available()


def get_name_embeddings(model, data):
    """สร้าง embeddings จากชื่ออาหาร"""
    if model is None or not SENTENCE_TRANSFORMERS_AVAILABLE:
        return np.array([])
    
    if os.path.exists(EMBEDDINGS_NAME_PATH):
        try:
            with open(EMBEDDINGS_NAME_PATH, 'rb') as f:
                return pickle.load(f)
        except Exception:
            pass
    
    if data.empty:
        return np.array([])
    
    texts = data['name'].fillna('').astype(str).tolist()
    
    with st.spinner("กำลังสร้างดัชนีชื่ออาหาร..."):
        embeddings = model.encode(texts, show_progress_bar=True)
    
    try:
        with open(EMBEDDINGS_NAME_PATH, 'wb') as f:
            pickle.dump(embeddings, f)
    except Exception as e:
        st.warning(f"ไม่สามารถบันทึก name embeddings: {e}")
    
    return embeddings


def get_ingredient_embeddings(model, data):
    """สร้าง embeddings จากส่วนผสม"""
    if model is None or not SENTENCE_TRANSFORMERS_AVAILABLE:
        return np.array([])
    
    if os.path.exists(EMBEDDINGS_INGREDIENT_PATH):
        try:
            with open(EMBEDDINGS_INGREDIENT_PATH, 'rb') as f:
                return pickle.load(f)
        except Exception:
            pass
    
    if data.empty:
        return np.array([])
    
    texts = data['ingredient'].fillna('').astype(str).tolist()
    
    with st.spinner("กำลังสร้างดัชนีส่วนผสม..."):
        embeddings = model.encode(texts, show_progress_bar=True)
    
    try:
        with open(EMBEDDINGS_INGREDIENT_PATH, 'wb') as f:
            pickle.dump(embeddings, f)
    except Exception as e:
        st.warning(f"ไม่สามารถบันทึก ingredient embeddings: {e}")
    
    return embeddings