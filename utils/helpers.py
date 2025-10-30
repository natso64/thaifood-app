"""
utils/helpers.py
ฟังก์ชันช่วยเหลือทั่วไป
"""

import numpy as np

def simple_cosine_similarity(query_vec, embeddings):
    """
    คำนวณ cosine similarity แบบง่าย (ใช้เมื่อไม่มี sklearn)
    """
    query_norm = query_vec / np.linalg.norm(query_vec)
    embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    similarities = np.dot(embeddings_norm, query_norm)
    return similarities


def check_sklearn_available():
    """ตรวจสอบว่ามี sklearn หรือไม่"""
    try:
        from sklearn.metrics.pairwise import cosine_similarity
        return True
    except ImportError:
        return False


def check_sentence_transformers_available():
    """ตรวจสอบว่ามี sentence-transformers หรือไม่"""
    try:
        from sentence_transformers import SentenceTransformer
        return True
    except ImportError:
        return False