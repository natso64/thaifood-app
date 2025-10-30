"""
search/nutrition_filter.py
กรองสูตรอาหารตามเกณฑ์โภชนาการ
"""

from typing import List, Dict
from nutrition.calculator import calculate_nutrition


# ===== Filter Criteria =====
FILTER_CRITERIA = {
    'calories_very_low': lambda n: n.get('calories', 999) < 100,
    'calories_low': lambda n: n.get('calories', 999) < 300,
    'calories_high': lambda n: n.get('calories', 0) > 500,
    'protein_very_high': lambda n: n.get('protein', 0) > 30,
    'protein_high': lambda n: n.get('protein', 0) > 15,
    'protein_low': lambda n: n.get('protein', 999) < 10,
    'fat_very_low': lambda n: n.get('fat', 999) < 3,
    'fat_low': lambda n: n.get('fat', 999) < 10,
    'fat_high': lambda n: n.get('fat', 0) > 20,
    'carbs_very_low': lambda n: n.get('carbs', 999) < 10,
    'carbs_low': lambda n: n.get('carbs', 999) < 30,
    'carbs_high': lambda n: n.get('carbs', 0) > 50,
    'fiber_high': lambda n: n.get('fiber', 0) > 5,
    'vitamin_a_high': lambda n: n.get('vitamin_a', 0) > 500,
    'vitamin_c_high': lambda n: n.get('vitamin_c', 0) > 30,
    'calcium_high': lambda n: n.get('calcium', 0) > 200,
    'iron_high': lambda n: n.get('iron', 0) > 3,
    'sodium_low': lambda n: n.get('sodium', 999) < 500,
}


def filter_recipes_by_nutrition(
    recipes_df,
    nutrition_df,
    selected_filters: List[str],
    match_mode: str = 'any',
    top_k: int = 10
) -> List[Dict]:
    """กรองสูตรอาหารตามเกณฑ์โภชนาการ"""
    
    if not selected_filters:
        return []
    
    filtered_results = []
    
    for idx, recipe in recipes_df.iterrows():
        nutrition_data = calculate_nutrition(
            recipe.get('ingredient', ''),
            nutrition_df
        )
        
        if not nutrition_data or 'total' not in nutrition_data:
            continue
        
        total = nutrition_data['total']
        matched_filters = []
        
        for filter_key in selected_filters:
            if filter_key in FILTER_CRITERIA:
                if FILTER_CRITERIA[filter_key](total):
                    matched_filters.append(filter_key)
        
        # ตรวจสอบ match mode
        if match_mode == 'all':
            if len(matched_filters) == len(selected_filters):
                score = len(matched_filters) * 10
            else:
                continue
        else:  # 'any'
            if len(matched_filters) == 0:
                continue
            score = len(matched_filters) * 5
        
        filtered_results.append({
            'recipe': recipe,
            'nutrition': nutrition_data,
            'score': score,
            'matched_filters': matched_filters,
            'match_percentage': (len(matched_filters) / len(selected_filters)) * 100,
            'index': idx
        })
    
    filtered_results = sorted(
        filtered_results,
        key=lambda x: (x['score'], x['match_percentage']),
        reverse=True
    )
    
    return filtered_results[:top_k]