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
    with st.spinner("กำลังดาวน์โหลดโมเดล ... (ใช้เวลาประมาณ 2-3 นาที)"):
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
        with open(EMBEDDINGS_INGREDIENT_PATH, 'wb') as f:
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

def search_recipes(query: str, model, data, embeddings, ingredient_embeddings, top_k: int = 5, search_mode: str = 'อัตโนมัติ', min_similarity: float = None):
    """
    search_mode options:
    - 'อัตโนมัติ': ใช้ AI search และถ้าผลลัพธ์ไม่ดีจะใช้ Fuzzy search เสริม (default)
    - 'AI Search เท่านั้น': ใช้ AI-based semantic search เท่านั้น
    - 'Fuzzy Search เท่านั้น': ใช้ Fuzzy string matching เท่านั้น
    """
    if data.empty:
        return []

    results = []
    
    # --- AI Search / Semantic Search ---
    if search_mode in ['อัตโนมัติ', 'AI Search เท่านั้น']:
        if model is not None and SENTENCE_TRANSFORMERS_AVAILABLE and len(embeddings) > 0:
            query_embedding = model.encode([query])
            
            if SKLEARN_AVAILABLE:
                similarities = cosine_similarity(query_embedding, embeddings)[0]
            else:
                similarities = simple_cosine_similarity(query_embedding[0], embeddings)
            
            # Use UI-provided min_similarity if available, otherwise default thresholds
            threshold = min_similarity if (min_similarity is not None) else 0.3
            top_indices = np.argsort(-similarities)[:top_k * 2]

            for idx in top_indices:
                if idx < len(data) and similarities[idx] >= threshold:
                    results.append({
                        'name': data.iloc[idx]['name'],
                        'similarity': float(similarities[idx]),
                        'ingredients': data.iloc[idx].get('ingredient', ''),
                        'method': data.iloc[idx].get('method', ''),
                        'index': int(idx),
                        'type': 'semantic'
                    })

    # --- Fuzzy Search ---
    # Trigger fuzzy search if:
    # 1. Mode is 'Fuzzy Search เท่านั้น'
    # 2. Mode is 'อัตโนมัติ' AND AI search had no/poor results or AI is unavailable.
    use_fuzzy = False
    if search_mode == 'Fuzzy Search เท่านั้น':
        use_fuzzy = True
    elif search_mode == 'อัตโนมัติ':
        fallback_threshold = min_similarity if (min_similarity is not None) else 0.4
        if not results or (results and results[0]['similarity'] < fallback_threshold) or model is None:
            use_fuzzy = True

    if use_fuzzy:
        fuzzy_results = fuzzy_search_recipes(query, data, top_k, min_similarity=min_similarity)
        
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
            
            results = sorted(unique_results, key=lambda x: x['similarity'], reverse=True)

    return results[:top_k]


def fuzzy_search_recipes(query: str, data, top_k: int = 5, min_similarity: float = None) -> List[Dict]:
    """Fuzzy search based on name and content.
    If min_similarity is provided, use it as the content matching threshold (0-1).
    """
    results = []
    
    # Phase 1: Direct name matching
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
            
            name_score = difflib.SequenceMatcher(None, query_lower, name).ratio()
            ingredient_words = ingredients.split()
            ingredient_score = max([difflib.SequenceMatcher(None, query_lower, word).ratio() 
                                   for word in ingredient_words] + [0]) if ingredient_words else 0
            method_words = method.split()
            method_score = max([difflib.SequenceMatcher(None, query_lower, word).ratio() 
                               for word in method_words] + [0]) if method_words else 0
            max_score = max(name_score, ingredient_score, method_score)
            
            threshold = min_similarity if (min_similarity is not None) else 0.4
            if max_score > threshold:
                results.append({
                    'name': row['name'],
                    'similarity': max_score,
                    'ingredients': row.get('ingredient', ''),
                    'method': row.get('method', ''),
                    'index': idx,
                    'type': 'content_match'
                })
    
    return sorted(results, key=lambda x: x['similarity'], reverse=True)[:top_k]
