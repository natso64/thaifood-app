"""
nutrition/parser.py
แยกส่วนผสมและปริมาณ
"""

import re
from typing import List, Tuple
from utils.constants import UNIT_CONVERSIONS


def parse_ingredient_amount(ingredient_text: str) -> List[Tuple[str, float]]:
    """
    แยกส่วนผสมและปริมาณ (กรัม)
    
    Returns: List of (ingredient_name, amount_in_grams)
    """
    ingredients = []
    lines = ingredient_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        pattern = r'(.+?)\s+(\d+(?:\.\d+)?)\s*(\S+)'
        match = re.search(pattern, line)
        
        if match:
            ingredient_name = match.group(1).strip()
            amount = float(match.group(2))
            unit = match.group(3).strip()
            
            if 'กรัม' in unit or 'g' in unit.lower():
                amount_in_grams = amount
            elif unit in UNIT_CONVERSIONS:
                amount_in_grams = amount * UNIT_CONVERSIONS[unit]
            else:
                amount_in_grams = amount * 100
            
            ingredients.append((ingredient_name, amount_in_grams))
        else:
            ingredients.append((line, 100.0))
    
    return ingredients