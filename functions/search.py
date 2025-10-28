import os
import pickle
import numpy as np
import streamlit as st
from functions.search_nomodel import get_tfidf_embeddings_from_column, simple_cosine_similarity


try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    cosine_similarity = None
    TfidfVectorizer = None
    SKLEARN_AVAILABLE = False

#EMBEDDINGS_PATH = "embeddings.pkl"
EMBEDDINGS_NAME_PATH = 'embeddings_name.pkl'
EMBEDDINGS_INGREDIENT_PATH = 'embeddings_ingredient.pkl'
MODEL_PATH = "model"
MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'

@st.cache_resource
def load_model():
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        return None
    if os.path.exists(MODEL_PATH):
        return SentenceTransformer(MODEL_PATH)
    with st.spinner("กำลังดาวน์โหลดโมเดล ${MODEL_NAME}... "):
        model = SentenceTransformer(MODEL_NAME)
        os.makedirs(MODEL_PATH, exist_ok=True)
        model.save(MODEL_PATH)
        return model
    
"""
@st.cache_data
def get_embeddings(_model, data):
    if _model is None or not SENTENCE_TRANSFORMERS_AVAILABLE:
        return get_tfidf_embeddings(data)
    if os.path.exists(EMBEDDINGS_PATH):
        try:
            with open(EMBEDDINGS_PATH, 'rb') as f:
                return pickle.load(f)
        except Exception:
            pass
    if data.empty:
        return np.array([])
    texts = []
    for _, row in data.iterrows():
        ingredient_text = str(row.get('ingredient', ''))
        method_text = str(row.get('method', ''))
        combined_text = f"{row['name']} {ingredient_text} {method_text}"
        texts.append(combined_text)
    with st.spinner("กำลังสร้างดัชนีการค้นหา..."):
        embeddings = _model.encode(texts)
    try:
        with open(EMBEDDINGS_PATH, 'wb') as f:
            pickle.dump(embeddings, f)
    except Exception:
        pass
    return embeddings
"""

# ======= สำหรับ NAME EMBEDDINGS =======
def get_name_embeddings(_model, data):
    """สร้าง embeddings จากชื่ออาหาร"""
    if _model is None or not SENTENCE_TRANSFORMERS_AVAILABLE:
        return get_tfidf_embeddings_from_column(data, 'name')
    
    # โหลดจากไฟล์ถ้ามี
    if os.path.exists(EMBEDDINGS_NAME_PATH):
        try:
            with open(EMBEDDINGS_NAME_PATH, 'rb') as f:
                return pickle.load(f)
        except Exception:
            pass
    
    if data.empty:
        return np.array([])
    
    # สร้าง embedding จากชื่อ
    texts = data['name'].fillna('').astype(str).tolist()
    
    with st.spinner("กำลังสร้างดัชนีชื่ออาหาร..."):
        embeddings = _model.encode(texts, show_progress_bar=True)
    
    # บันทึกลงไฟล์
    try:
        with open(EMBEDDINGS_NAME_PATH, 'wb') as f:
            pickle.dump(embeddings, f)
    except Exception as e:
        st.warning(f"ไม่สามารถบันทึก name embeddings: {e}")
    
    return embeddings


# ======= สำหรับ INGREDIENT EMBEDDINGS =======
def get_ingredient_embeddings(_model, data):
    """สร้าง embeddings จากส่วนผสม"""
    if _model is None or not SENTENCE_TRANSFORMERS_AVAILABLE:
        return get_tfidf_embeddings_from_column(data, 'ingredient')
    
    # โหลดจากไฟล์ถ้ามี
    if os.path.exists(EMBEDDINGS_INGREDIENT_PATH):
        try:
            with open(EMBEDDINGS_INGREDIENT_PATH, 'rb') as f:
                return pickle.load(f)
        except Exception:
            pass
    
    if data.empty:
        return np.array([])
    
    # สร้าง embedding จากส่วนผสม
    texts = data['ingredient'].fillna('').astype(str).tolist()
    
    with st.spinner("กำลังสร้างดัชนีส่วนผสม..."):
        embeddings = _model.encode(texts, show_progress_bar=True)
    
    # บันทึกลงไฟล์
    try:
        with open(EMBEDDINGS_INGREDIENT_PATH, 'wb') as f:
            pickle.dump(embeddings, f)
    except Exception as e:
        st.warning(f"ไม่สามารถบันทึก ingredient embeddings: {e}")
    
    return embeddings





def search_recipes(query: str, model, data, name_embeddings, ingredient_embeddings, 
                   top_k: int = 5, min_similarity: float = 0.3, exact_match_threshold: float = 0.95):
    """
    ค้นหาสูตรอาหารด้วย Cosine Similarity
    - เปรียบเทียบชื่อก่อน ถ้าตรงกัน 100% (หรือใกล้เคียง) แสดงก่อน
    - จากนั้นค่อยค้นหาจากส่วนผสม
    
    Parameters:
    - query: คำค้นหา
    - model: โมเดลสำหรับ encode text
    - data: DataFrame ของสูตรอาหาร
    - name_embeddings: embeddings ของชื่ออาหาร
    - ingredient_embeddings: embeddings ของส่วนผสม
    - top_k: จำนวนผลลัพธ์ที่ต้องการ
    - min_similarity: ค่า threshold ขั้นต่ำสำหรับส่วนผสม (default: 0.3)
    - exact_match_threshold: ค่า threshold สำหรับถือว่าตรงกัน 100% (default: 0.95)
    """
    if data.empty or model is None:
        return []

    results = []
    exact_matches = []
    similar_matches = []
    
    # Encode คำค้นหา
    query_embedding = model.encode([query])
    
    # ======= ขั้นตอนที่ 1: ค้นหาจากชื่ออาหาร =======
    if len(name_embeddings) > 0:
        if SKLEARN_AVAILABLE:
            name_similarities = cosine_similarity(query_embedding, name_embeddings)[0]
        else:
            name_similarities = simple_cosine_similarity(query_embedding[0], name_embeddings)
        
        # แยก exact matches (ตรงกัน 100% หรือใกล้เคียง)
        for idx in range(len(data)):
            if idx < len(name_similarities):
                similarity = float(name_similarities[idx])
                
                result = {
                    'name': data.iloc[idx]['name'],
                    'similarity': similarity,
                    'ingredients': data.iloc[idx].get('ingredient', ''),
                    'method': data.iloc[idx].get('method', ''),
                    'index': int(idx),
                    'type': 'name_exact' if similarity >= exact_match_threshold else 'name_similar'
                }
                
                if similarity >= exact_match_threshold:
                    exact_matches.append(result)
    
    # ======= ขั้นตอนที่ 2: ค้นหาจากส่วนผสม =======
    if len(ingredient_embeddings) > 0:
        if SKLEARN_AVAILABLE:
            ingredient_similarities = cosine_similarity(query_embedding, ingredient_embeddings)[0]
        else:
            ingredient_similarities = simple_cosine_similarity(query_embedding[0], ingredient_embeddings)
        
        # เอาเฉพาะที่เกิน threshold และไม่ซ้ำกับ exact matches
        exact_indices = {match['index'] for match in exact_matches}
        
        top_indices = np.argsort(-ingredient_similarities)[:top_k * 3]
        
        for idx in top_indices:
            if idx < len(data) and ingredient_similarities[idx] >= min_similarity:
                if idx not in exact_indices:  # ไม่ซ้ำกับ exact matches
                    similar_matches.append({
                        'name': data.iloc[idx]['name'],
                        'similarity': float(ingredient_similarities[idx]),
                        'ingredients': data.iloc[idx].get('ingredient', ''),
                        'method': data.iloc[idx].get('method', ''),
                        'index': int(idx),
                        'type': 'ingredient_similar'
                    })
    
    # ======= รวมผลลัพธ์: Exact matches ก่อน จากนั้น Similar matches =======
    # เรียง exact matches ตาม similarity
    exact_matches = sorted(exact_matches, key=lambda x: x['similarity'], reverse=True)
    
    # เรียง similar matches ตาม similarity
    similar_matches = sorted(similar_matches, key=lambda x: x['similarity'], reverse=True)
    
    # รวมกัน: exact matches ก่อน
    results = exact_matches + similar_matches
    
    return results[:top_k]