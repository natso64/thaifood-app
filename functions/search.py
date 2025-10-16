import os
import pickle
import numpy as np
import streamlit as st
import difflib
import re
from typing import Dict, List

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

EMBEDDINGS_PATH = "embeddings.pkl"
EMBEDDINGS_INGREDIENT_PATH = "embeddings_ingredient.pkl"
MODEL_PATH = "model"

@st.cache_resource
def load_model():
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        return None
    if os.path.exists(MODEL_PATH):
        return SentenceTransformer(MODEL_PATH)
    with st.spinner("กำลังดาวน์โหลดโมเดล AI... (ใช้เวลาประมาณ 2-3 นาที)"):
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        os.makedirs(MODEL_PATH, exist_ok=True)
        model.save(MODEL_PATH)
        return model

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
    with st.spinner("กำลังสร้างดัชนีการค้นหา... (ใช้เวลาประมาณ 1-2 นาที)"):
        embeddings = _model.encode(texts)
    try:
        with open(EMBEDDINGS_PATH, 'wb') as f:
            pickle.dump(embeddings, f)
    except Exception:
        pass
    return embeddings
    
@st.cache_data
def get_ingredient_embeddings(_model, data):
    if _model is None or not SENTENCE_TRANSFORMERS_AVAILABLE:
        return get_tfidf_embeddings(data['ingredient'])
    
    if os.path.exists(EMBEDDINGS_INGREDIENT_PATH):
        try:
            with open(EMBEDDINGS_INGREDIENT_PATH, 'rb') as f:
                return pickle.load(f)
        except Exception:
            pass
    
    if data.empty:
        return np.array([])
    
    # สร้าง embedding เฉพาะ ingredient
    texts = data['ingredient'].fillna('').astype(str).tolist()
    
    with st.spinner("กำลังสร้างดัชนีส่วนผสม..."):
        embeddings = _model.encode(texts)
    
    try:
        with open(embeddings_path, 'wb') as f:
            pickle.dump(embeddings, f)
    except Exception:
        pass
    
    return embeddings

@st.cache_data
def get_tfidf_embeddings(data):
    if data.empty:
        return np.array([])
    texts = []
    for _, row in data.iterrows():
        ingredient_text = str(row.get('ingredient', ''))
        method_text = str(row.get('method', ''))
        combined_text = f"{row['name']} {ingredient_text} {method_text}"
        texts.append(combined_text)
    if SKLEARN_AVAILABLE:
        vectorizer = TfidfVectorizer(max_features=1000)
        embeddings = vectorizer.fit_transform(texts).toarray()
        return embeddings
    else:
        return create_simple_embeddings(texts)

def create_simple_embeddings(texts):
    all_words = set()
    processed_texts = []
    for text in texts:
        words = re.findall(r'\w+', text.lower())
        processed_texts.append(words)
        all_words.update(words)
    vocab = list(all_words)[:1000]
    embeddings = []
    for words in processed_texts:
        vector = [words.count(word) for word in vocab]
        embeddings.append(vector)
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

def search_recipes(query: str, model, data, embeddings, ingredient_embeddings=None, top_k: int = 5, search_mode: str = 'combined'):
    """
    search_mode options:
    - 'combined': ค้นหาจากทั้งชื่อ วัตถุดิบ และวิธีทำ (default)
    - 'ingredient': ค้นหาเฉพาะจากวัตถุดิบ
    - 'name': ค้นหาเฉพาะจากชื่อเมนู
    """
    if data.empty:
        return []
    
    results = []
    
    # เลือก embeddings ตาม search_mode
    if search_mode == 'ingredient' and ingredient_embeddings is not None:
        selected_embeddings = ingredient_embeddings
    else:
        selected_embeddings = embeddings
    
    # Semantic search
    if model is not None and SENTENCE_TRANSFORMERS_AVAILABLE and len(selected_embeddings) > 0:
        query_embedding = model.encode([query])
        
        if SKLEARN_AVAILABLE:
            similarities = cosine_similarity(query_embedding, selected_embeddings)[0]
        else:
            similarities = simple_cosine_similarity(query_embedding[0], selected_embeddings)
        
        # ปรับ threshold ตาม search_mode
        threshold = 0.25 if search_mode == 'ingredient' else 0.3
        
        top_indices = np.argsort(-similarities)[:top_k * 2]  # เอาเผื่อกรอง
        
        for idx in top_indices:
            if idx < len(data) and similarities[idx] >= threshold:
                results.append({
                    'name': data.iloc[idx]['name'],
                    'similarity': float(similarities[idx]),
                    'ingredients': data.iloc[idx].get('ingredient', ''),
                    'method': data.iloc[idx].get('method', ''),
                    'index': int(idx),
                    'type': 'semantic',
                    'search_mode': search_mode
                })
    
    # Fallback to fuzzy search if results are poor or no model
    if not results or (results and results[0]['similarity'] < 0.3) or model is None:
        fuzzy_results = fuzzy_search_recipes(query, data, top_k, search_mode)
        
        if not results:
            results = fuzzy_results
        else:
            # Combine and deduplicate
            all_results = results + fuzzy_results
            seen_indices = set()
            unique_results = []
            
            for result in all_results:
                if result['index'] not in seen_indices:
                    unique_results.append(result)
                    seen_indices.add(result['index'])
            
            # Sort by similarity and take top_k
            results = sorted(unique_results, key=lambda x: x['similarity'], reverse=True)[:top_k]
    
    return results[:top_k]


def fuzzy_search_recipes(query: str, data, top_k: int = 5, search_mode: str = 'combined') -> List[Dict]:
    """Fuzzy search with mode support"""
    results = []
    
    # Phase 1: Direct name matching
    if search_mode in ['combined', 'name']:
        food_names = data['name'].tolist()
        close_matches = difflib.get_close_matches(query, food_names, n=top_k, cutoff=0.3)
        
        for match in close_matches:
            idx = data[data['name'] == match].index[0]
            similarity = difflib.SequenceMatcher(None, query.lower(), match.lower()).ratio()
            results.append({
                'name': match,
                'similarity': similarity,
                'ingredients': data.iloc[idx].get('ingredient', ''),
                'method': data.iloc[idx].get('method', ''),
                'index': idx,
                'type': 'fuzzy'
            })
    
    # Phase 2: Content matching
    if len(results) < top_k:
        for idx, row in data.iterrows():
            if idx in [r['index'] for r in results]:
                continue
            
            name = str(row['name']).lower()
            ingredients = str(row.get('ingredient', '')).lower()
            method = str(row.get('method', '')).lower()
            query_lower = query.lower()
            
            # Calculate scores based on search_mode
            if search_mode == 'ingredient':
                # Focus only on ingredients
                ingredient_words = ingredients.split()
                ingredient_score = max([difflib.SequenceMatcher(None, query_lower, word).ratio() 
                                       for word in ingredient_words] + [0])
                max_score = ingredient_score
                
            elif search_mode == 'name':
                # Focus only on name
                name_score = difflib.SequenceMatcher(None, query_lower, name).ratio()
                max_score = name_score
                
            else:  # combined
                name_score = difflib.SequenceMatcher(None, query_lower, name).ratio()
                ingredient_score = max([difflib.SequenceMatcher(None, query_lower, word).ratio() 
                                       for word in ingredients.split()] + [0])
                method_score = max([difflib.SequenceMatcher(None, query_lower, word).ratio() 
                                   for word in method.split()] + [0])
                max_score = max(name_score, ingredient_score, method_score)
            
            if max_score > 0.4:
                results.append({
                    'name': row['name'],
                    'similarity': max_score,
                    'ingredients': row.get('ingredient', ''),
                    'method': row.get('method', ''),
                    'index': idx,
                    'type': 'content_match'
                })
    
    return sorted(results, key=lambda x: x['similarity'], reverse=True)[:top_k]
