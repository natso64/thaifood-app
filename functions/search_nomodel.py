# ======= สำหรับ INGREDIENT EMBEDDINGS , COSINE SIMILARITY =======

import numpy as np
import streamlit as st
from functions.search import SKLEARN_AVAILABLE
from sklearn.feature_extraction.text import TfidfVectorizer


# ======= TF-IDF FALLBACK (เมื่อไม่มี model) =======
@st.cache_data
def get_tfidf_embeddings_from_column(data, column_name):
    """
    สร้าง TF-IDF embeddings จาก column ที่ระบุ
    
    Parameters:
    - data: DataFrame
    - column_name: ชื่อ column ที่ต้องการสร้าง embedding ('name' หรือ 'ingredient')
    """
    if data.empty:
        return np.array([])
    
    # ดึง text จาก column ที่ระบุ
    texts = data[column_name].fillna('').astype(str).tolist()
    
    if SKLEARN_AVAILABLE:
        try:
            vectorizer = TfidfVectorizer(max_features=1000)
            embeddings = vectorizer.fit_transform(texts).toarray()
            return embeddings
        except Exception as e:
            st.warning(f"TF-IDF error: {e}")
            return create_simple_embeddings(texts)
    else:
        return create_simple_embeddings(texts)


def create_simple_embeddings(texts):
    """
    สร้าง embeddings แบบง่าย (เมื่อไม่มี sklearn)
    ใช้ character frequency เป็น features
    """
    if not texts:
        return np.array([])
    
    # สร้าง vocabulary จากตัวอักษรทั้งหมด
    all_chars = set(''.join(texts))
    char_to_idx = {char: idx for idx, char in enumerate(sorted(all_chars))}
    
    # สร้าง embeddings
    embeddings = []
    for text in texts:
        vec = np.zeros(len(char_to_idx))
        for char in text:
            if char in char_to_idx:
                vec[char_to_idx[char]] += 1
        # Normalize
        if vec.sum() > 0:
            vec = vec / vec.sum()
        embeddings.append(vec)
    
    return np.array(embeddings)

def simple_cosine_similarity(query_vec, embeddings):
    similarities = []
    query_norm = np.linalg.norm(query_vec)
    for embedding in embeddings:
        if query_norm == 0 or np.linalg.norm(embedding) == 0:
            similarities.append(0)
        else:
            dot_product = np.dot(query_vec, embedding)
            similarity = dot_product / (query_norm * np.linalg.norm(embedding))
            similarities.append(similarity)
    return np.array(similarities)