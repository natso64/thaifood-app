"""
search/semantic_search.py
ค้นหาด้วย Semantic/Cosine Similarity
"""

import numpy as np
from utils.helpers import check_sklearn_available, simple_cosine_similarity
from config import DEFAULT_TOP_K, DEFAULT_MIN_SIMILARITY, DEFAULT_EXACT_MATCH_THRESHOLD

SKLEARN_AVAILABLE = check_sklearn_available()

if SKLEARN_AVAILABLE:
    from sklearn.metrics.pairwise import cosine_similarity


def search_recipes(
    query: str,
    model,
    data,
    name_embeddings,
    ingredient_embeddings,
    top_k: int = DEFAULT_TOP_K,
    min_similarity: float = DEFAULT_MIN_SIMILARITY,
    exact_match_threshold: float = DEFAULT_EXACT_MATCH_THRESHOLD
):
    """
    ค้นหาสูตรอาหารด้วย Cosine Similarity
    - เปรียบเทียบชื่อก่อน ถ้าตรงกัน 100% แสดงก่อน
    - จากนั้นค่อยค้นหาจากส่วนผสม
    """
    if data.empty or model is None:
        return []

    exact_matches = []
    similar_matches = []
    
    query_embedding = model.encode([query])
    
    # ===== ค้นหาจากชื่ออาหาร =====
    if len(name_embeddings) > 0:
        if SKLEARN_AVAILABLE:
            name_similarities = cosine_similarity(query_embedding, name_embeddings)[0]
        else:
            name_similarities = simple_cosine_similarity(query_embedding[0], name_embeddings)
        
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
    
    # ===== ค้นหาจากส่วนผสม =====
    if len(ingredient_embeddings) > 0:
        if SKLEARN_AVAILABLE:
            ingredient_similarities = cosine_similarity(query_embedding, ingredient_embeddings)[0]
        else:
            ingredient_similarities = simple_cosine_similarity(query_embedding[0], ingredient_embeddings)
        
        exact_indices = {match['index'] for match in exact_matches}
        top_indices = np.argsort(-ingredient_similarities)[:top_k * 3]
        
        for idx in top_indices:
            if idx < len(data) and ingredient_similarities[idx] >= min_similarity:
                if idx not in exact_indices:
                    similar_matches.append({
                        'name': data.iloc[idx]['name'],
                        'similarity': float(ingredient_similarities[idx]),
                        'ingredients': data.iloc[idx].get('ingredient', ''),
                        'method': data.iloc[idx].get('method', ''),
                        'index': int(idx),
                        'type': 'ingredient_similar'
                    })
    
    # ===== รวมผลลัพธ์ =====
    exact_matches = sorted(exact_matches, key=lambda x: x['similarity'], reverse=True)
    similar_matches = sorted(similar_matches, key=lambda x: x['similarity'], reverse=True)
    results = exact_matches + similar_matches
    
    return results[:top_k]