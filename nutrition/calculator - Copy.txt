"""
nutrition/calculator.py
คำนวณโภชนาการ
"""

import pandas as pd
from typing import Dict
from nutrition.parser import parse_ingredient_amount


def calculate_nutrition(ingredient_text: str, nutrition_df: pd.DataFrame) -> Dict:
    """คำนวณโภชนาการรวมจากส่วนผสม"""
    
    if nutrition_df.empty:
        return {}
    
    ingredients = parse_ingredient_amount(ingredient_text)
    
    total_nutrition = {
        'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0,
        'fiber': 0, 'vitamin_a': 0, 'vitamin_c': 0,
        'vitamin_b1': 0, 'vitamin_b2': 0, 'calcium': 0,
        'iron': 0, 'potassium': 0, 'sodium': 0
    }
    
    matched_ingredients = []
    
    for ingredient_name, amount_grams in ingredients:
        ingredient_lower = ingredient_name.lower().strip()
        
        matches = nutrition_df[nutrition_df['ingredient_lower'] == ingredient_lower]
        
        if matches.empty:
            matches = nutrition_df[nutrition_df['ingredient_lower'].str.contains(ingredient_lower, na=False)]
        
        if matches.empty:
            for idx, row in nutrition_df.iterrows():
                if row['ingredient_lower'] in ingredient_lower:
                    matches = nutrition_df.iloc[[idx]]
                    break
        
        if not matches.empty:
            nutri_data = matches.iloc[0]
            ratio = amount_grams / 100.0
            
            for nutrient in total_nutrition.keys():
                if nutrient in nutri_data:
                    value = nutri_data[nutrient]
                    if pd.notna(value):
                        total_nutrition[nutrient] += float(value) * ratio
            
            matched_ingredients.append({
                'name': ingredient_name,
                'amount': amount_grams,
                'matched_db': nutri_data['ingredient']
            })
    
    return {
        'total': total_nutrition,
        'matched_ingredients': matched_ingredients,
        'total_weight': sum(amount for _, amount in ingredients)
    }