import re
from typing import Dict


class SimpleNutritionCalculator:
    """Simple nutrition calculator using heuristic per-100g values."""

    def __init__(self):
        self.basic_nutrition = {
            'ข้าว': {
                'calories': 130, 'protein': 2.7, 'fat': 0.3, 'carbs': 28, 'fiber': 0.4,
                'vitamin_c': 0, 'calcium': 28, 'iron': 0.8, 'magnesium': 25, 'phosphorus': 115,
                'potassium': 115, 'zinc': 1.1, 'sodium': 5, 'vitamin_b6': 0.164, 'vitamin_k': 0.1,
                'vitamin_b1': 0.07, 'vitamin_b2': 0.049, 'vitamin_b3': 1.6, 'folate': 8,
                'vitamin_a': 0, 'vitamin_b12': 0, 'vitamin_e': 0.11
            },
            'เนื้อหมู': {
                'calories': 242, 'protein': 27, 'fat': 14, 'carbs': 0, 'fiber': 0,
                'vitamin_c': 0.7, 'calcium': 19, 'iron': 0.9, 'magnesium': 24, 'phosphorus': 200,
                'potassium': 423, 'zinc': 2.9, 'sodium': 62, 'vitamin_b6': 0.464, 'vitamin_k': 0,
                'vitamin_b1': 0.658, 'vitamin_b2': 0.321, 'vitamin_b3': 4.99, 'folate': 2,
                'vitamin_a': 2, 'vitamin_b12': 0.7, 'vitamin_e': 0.3
            },
            'ไก่': {
                'calories': 165, 'protein': 31, 'fat': 3.6, 'carbs': 0, 'fiber': 0,
                'vitamin_c': 1.6, 'calcium': 15, 'iron': 1.3, 'magnesium': 25, 'phosphorus': 228,
                'potassium': 256, 'zinc': 1.3, 'sodium': 70, 'vitamin_b6': 0.35, 'vitamin_k': 0,
                'vitamin_b1': 0.063, 'vitamin_b2': 0.114, 'vitamin_b3': 9.91, 'folate': 6,
                'vitamin_a': 48, 'vitamin_b12': 0.34, 'vitamin_e': 0.27
            },
            'กุ้ง': {
                'calories': 106, 'protein': 20, 'fat': 1.7, 'carbs': 0.9, 'fiber': 0,
                'vitamin_c': 2.1, 'calcium': 70, 'iron': 0.5, 'magnesium': 37, 'phosphorus': 205,
                'potassium': 259, 'zinc': 1.6, 'sodium': 111, 'vitamin_b6': 0.11, 'vitamin_k': 0.3,
                'vitamin_b1': 0.04, 'vitamin_b2': 0.061, 'vitamin_b3': 2.85, 'folate': 18,
                'vitamin_a': 102, 'vitamin_b12': 1.11, 'vitamin_e': 1.01
            },
            'ปลา': {
                'calories': 206, 'protein': 22, 'fat': 12, 'carbs': 0, 'fiber': 0,
                'vitamin_c': 0.9, 'calcium': 18, 'iron': 0.2, 'magnesium': 35, 'phosphorus': 217,
                'potassium': 414, 'zinc': 0.4, 'sodium': 59, 'vitamin_b6': 0.468, 'vitamin_k': 0,
                'vitamin_b1': 0.15, 'vitamin_b2': 0.155, 'vitamin_b3': 4.1, 'folate': 15,
                'vitamin_a': 158, 'vitamin_b12': 4.45, 'vitamin_e': 0.7
            },
            'ไข่': {
                'calories': 155, 'protein': 13, 'fat': 11, 'carbs': 1.1, 'fiber': 0,
                'vitamin_c': 0, 'calcium': 56, 'iron': 1.75, 'magnesium': 12, 'phosphorus': 198,
                'potassium': 138, 'zinc': 1.29, 'sodium': 142, 'vitamin_b6': 0.17, 'vitamin_k': 0.3,
                'vitamin_b1': 0.04, 'vitamin_b2': 0.457, 'vitamin_b3': 0.075, 'folate': 47,
                'vitamin_a': 540, 'vitamin_b12': 0.89, 'vitamin_e': 1.05
            },
            'มะเขือเทศ': {
                'calories': 18, 'protein': 0.9, 'fat': 0.2, 'carbs': 3.9, 'fiber': 1.2,
                'vitamin_c': 14, 'calcium': 10, 'iron': 0.3, 'magnesium': 11, 'phosphorus': 24,
                'potassium': 237, 'zinc': 0.17, 'sodium': 5, 'vitamin_b6': 0.08, 'vitamin_k': 7.9,
                'vitamin_b1': 0.037, 'vitamin_b2': 0.019, 'vitamin_b3': 0.594, 'folate': 15,
                'vitamin_a': 833, 'vitamin_b12': 0, 'vitamin_e': 0.54
            },
            'หอมใหญ่': {
                'calories': 40, 'protein': 1.1, 'fat': 0.1, 'carbs': 9.3, 'fiber': 1.7,
                'vitamin_c': 7.4, 'calcium': 23, 'iron': 0.21, 'magnesium': 10, 'phosphorus': 29,
                'potassium': 146, 'zinc': 0.17, 'sodium': 4, 'vitamin_b6': 0.12, 'vitamin_k': 0.4,
                'vitamin_b1': 0.046, 'vitamin_b2': 0.027, 'vitamin_b3': 0.116, 'folate': 19,
                'vitamin_a': 2, 'vitamin_b12': 0, 'vitamin_e': 0.02
            },
            'กระเทียม': {
                'calories': 149, 'protein': 6.4, 'fat': 0.5, 'carbs': 33, 'fiber': 2.1,
                'vitamin_c': 31.2, 'calcium': 181, 'iron': 1.7, 'magnesium': 25, 'phosphorus': 153,
                'potassium': 401, 'zinc': 1.16, 'sodium': 17, 'vitamin_b6': 1.235, 'vitamin_k': 1.7,
                'vitamin_b1': 0.2, 'vitamin_b2': 0.11, 'vitamin_b3': 0.7, 'folate': 3,
                'vitamin_a': 9, 'vitamin_b12': 0, 'vitamin_e': 0.08
            },
            'พริก': {
                'calories': 40, 'protein': 1.9, 'fat': 0.4, 'carbs': 7.3, 'fiber': 1.5,
                'vitamin_c': 144, 'calcium': 18, 'iron': 1.0, 'magnesium': 25, 'phosphorus': 46,
                'potassium': 340, 'zinc': 0.3, 'sodium': 7, 'vitamin_b6': 0.28, 'vitamin_k': 14,
                'vitamin_b1': 0.09, 'vitamin_b2': 0.09, 'vitamin_b3': 0.95, 'folate': 23,
                'vitamin_a': 952, 'vitamin_b12': 0, 'vitamin_e': 0.69
            },
            'น้ำมัน': {
                'calories': 884, 'protein': 0, 'fat': 100, 'carbs': 0, 'fiber': 0,
                'vitamin_c': 0, 'calcium': 0, 'iron': 0, 'magnesium': 0, 'phosphorus': 0,
                'potassium': 0, 'zinc': 0, 'sodium': 0, 'vitamin_b6': 0, 'vitamin_k': 60,
                'vitamin_b1': 0, 'vitamin_b2': 0, 'vitamin_b3': 0, 'folate': 0,
                'vitamin_a': 0, 'vitamin_b12': 0, 'vitamin_e': 14.35
            },
            'น้ำตาล': {
                'calories': 387, 'protein': 0, 'fat': 0, 'carbs': 100, 'fiber': 0,
                'vitamin_c': 0, 'calcium': 1, 'iron': 0.01, 'magnesium': 0, 'phosphorus': 0,
                'potassium': 2, 'zinc': 0.01, 'sodium': 1, 'vitamin_b6': 0, 'vitamin_k': 0,
                'vitamin_b1': 0, 'vitamin_b2': 0, 'vitamin_b3': 0, 'folate': 0,
                'vitamin_a': 0, 'vitamin_b12': 0, 'vitamin_e': 0
            },
            'เกลือ': {
                'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0, 'fiber': 0,
                'vitamin_c': 0, 'calcium': 24, 'iron': 0.33, 'magnesium': 290, 'phosphorus': 0,
                'potassium': 8, 'zinc': 0.1, 'sodium': 38758, 'vitamin_b6': 0, 'vitamin_k': 0,
                'vitamin_b1': 0, 'vitamin_b2': 0, 'vitamin_b3': 0, 'folate': 0,
                'vitamin_a': 0, 'vitamin_b12': 0, 'vitamin_e': 0
            },
        }

    def estimate_ingredient_amount(self, ingredient_text: str) -> float:
        numbers = re.findall(r'(\d+(?:\.\d+)?)', ingredient_text)
        if numbers:
            amount = float(numbers[0])
            if any(unit in ingredient_text for unit in ['กิโลกรัม', 'กก.', 'kg']):
                return amount * 1000
            elif any(unit in ingredient_text for unit in ['กรัม', 'ก.', 'g']):
                return amount
            elif any(unit in ingredient_text for unit in ['ช้อนโต๊ะ', 'ช้อนใหญ่']):
                return amount * 15
            elif any(unit in ingredient_text for unit in ['ช้อนชา', 'ช้อนเล็ก']):
                return amount * 5
            elif any(unit in ingredient_text for unit in ['ถ้วย', 'ถ้วยตวง']):
                return amount * 200
        if any(word in ingredient_text for word in ['เล็กน้อย', 'นิด']):
            return 5
        elif any(word in ingredient_text for word in ['กลาง', 'ปานกลาง']):
            return 30
        elif any(word in ingredient_text for word in ['มาก', 'เยอะ']):
            return 50
        return 20

    def find_nutrition_match(self, ingredient: str) -> Dict:
        ingredient_lower = ingredient.lower()
        for key, nutrition in self.basic_nutrition.items():
            if key in ingredient or any(word in ingredient_lower for word in key.split()):
                return nutrition
        if any(word in ingredient_lower for word in ['เนื้อ', 'หมู', 'วัว']):
            return self.basic_nutrition['เนื้อหมู']
        elif any(word in ingredient_lower for word in ['ไก่', 'เป็ด']):
            return self.basic_nutrition['ไก่']
        elif any(word in ingredient_lower for word in ['ปลา', 'กุ้ง', 'ปู', 'หอย']):
            return self.basic_nutrition['ปลา']
        elif any(word in ingredient_lower for word in ['ผัก', 'ใบ']):
            return {
                'calories': 25, 'protein': 2, 'fat': 0.3, 'carbs': 4, 'fiber': 2.6,
                'vitamin_c': 28, 'calcium': 40, 'iron': 1.5, 'magnesium': 12, 'phosphorus': 25,
                'potassium': 194, 'zinc': 0.2, 'sodium': 12, 'vitamin_b6': 0.074, 'vitamin_k': 108,
                'vitamin_b1': 0.03, 'vitamin_b2': 0.086, 'vitamin_b3': 0.425, 'folate': 62,
                'vitamin_a': 469, 'vitamin_b12': 0, 'vitamin_e': 0.73
            }
        elif any(word in ingredient_lower for word in ['น้ำมัน', 'มัน']):
            return self.basic_nutrition['น้ำมัน']
        else:
            return {
                'calories': 30, 'protein': 1, 'fat': 0.5, 'carbs': 6, 'fiber': 1,
                'vitamin_c': 5, 'calcium': 20, 'iron': 0.5, 'magnesium': 10, 'phosphorus': 15,
                'potassium': 100, 'zinc': 0.1, 'sodium': 5, 'vitamin_b6': 0.05, 'vitamin_k': 2,
                'vitamin_b1': 0.02, 'vitamin_b2': 0.03, 'vitamin_b3': 0.2, 'folate': 10,
                'vitamin_a': 50, 'vitamin_b12': 0, 'vitamin_e': 0.2
            }

    def calculate_recipe_nutrition(self, ingredients_text: str) -> Dict:
        total = {
            'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0, 'fiber': 0,
            'vitamin_c': 0, 'calcium': 0, 'iron': 0, 'magnesium': 0, 'phosphorus': 0,
            'potassium': 0, 'zinc': 0, 'sodium': 0, 'vitamin_b6': 0, 'vitamin_k': 0,
            'vitamin_b1': 0, 'vitamin_b2': 0, 'vitamin_b3': 0, 'folate': 0,
            'vitamin_a': 0, 'vitamin_b12': 0, 'vitamin_e': 0
        }
        if not ingredients_text:
            return total
        ingredients = [line.strip() for line in ingredients_text.split('\n') if line.strip()]
        for ingredient in ingredients:
            clean_ingredient = re.sub(r'^[-•*]\s*', '', ingredient)
            amount_g = self.estimate_ingredient_amount(clean_ingredient)
            nutrition = self.find_nutrition_match(clean_ingredient)
            multiplier = amount_g / 100.0
            for nutrient in total.keys():
                total[nutrient] += nutrition.get(nutrient, 0) * multiplier
        return total


