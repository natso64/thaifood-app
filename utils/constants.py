"""
utils/constants.py
ค่าคงที่ต่างๆ เช่น keywords, units, ชื่อภาษาไทย
"""

# ===== Nutrition Keywords for Search =====
NUTRITION_KEYWORDS = {
    'calories_very_low': ['แคลอรี่ต่ำมาก'],
    'calories_low': ['แคลอรี่ต่ำ'],
    'calories_high': ['แคลอรี่สูง'],
    'protein_very_high': ['โปรตีนสูงมาก'],
    'protein_high': ['โปรตีนสูง'],
    'protein_low': ['โปรตีนต่ำ'],
    'fat_very_low': ['ไขมันต่ำมาก'],
    'fat_low': ['ไขมันต่ำ'],
    'fat_high': ['ไขมันสูง'],
    'carbs_very_low': ['คาร์โบต่ำมาก'],
    'carbs_low': ['คาร์โบต่ำ'],
    'carbs_high': ['คาร์โบสูง'],
    'fiber_high': ['ใยอาหารสูง'],
    'vitamin_a_high': ['วิตามินเอ'],
    'vitamin_c_high': ['วิตามินซี'],
    'calcium_high': ['แคลเซียม'],
    'iron_high': ['ธาตุเหล็ก'],
    'sodium_low': ['โซเดียมต่ำ'],
}

# ===== Nutrition Filter Groups for UI =====
NUTRITION_FILTER_GROUPS = {
    'แคลอรี่': {
        'แคลอรี่ต่ำมาก (< 100 kcal)': 'calories_very_low',
        'แคลอรี่ต่ำ (< 300 kcal)': 'calories_low',
        'แคลอรี่สูง (> 500 kcal)': 'calories_high',
    },
    'โปรตีน': {
        'โปรตีนสูงมาก (> 30g)': 'protein_very_high',
        'โปรตีนสูง (> 15g)': 'protein_high',
        'โปรตีนต่ำ (< 10g)': 'protein_low',
    },
    'ไขมัน': {
        'ไขมันต่ำมาก (< 3g)': 'fat_very_low',
        'ไขมันต่ำ (< 10g)': 'fat_low',
        'ไขมันสูง (> 20g)': 'fat_high',
    },
    'คาร์โบไฮเดรต': {
        'คาร์โบต่ำมาก / Keto (< 10g)': 'carbs_very_low',
        'คาร์โบต่ำ (< 30g)': 'carbs_low',
        'คาร์โบสูง (> 50g)': 'carbs_high',
    },
    'วิตามินและแร่ธาตุ': {
        'ใยอาหารสูง (> 5g)': 'fiber_high',
        'วิตามินเอสูง (> 500µg)': 'vitamin_a_high',
        'วิตามินซีสูง (> 30mg)': 'vitamin_c_high',
        'แคลเซียมสูง (> 200mg)': 'calcium_high',
        'เหล็กสูง (> 3mg)': 'iron_high',
        'โซเดียมต่ำ (< 500mg)': 'sodium_low',
    },
}

# ===== Thai Names for Nutrition =====
THAI_NAMES = {
    'calories': 'แคลอรี่',
    'protein': 'โปรตีน',
    'carbs': 'คาร์โบไฮเดรต',
    'fat': 'ไขมัน',
    'fiber': 'ใยอาหาร',
    'vitamin_a': 'วิตามินเอ',
    'vitamin_c': 'วิตามินซี',
    'vitamin_b1': 'วิตามินบี1',
    'vitamin_b2': 'วิตามินบี2',
    'calcium': 'แคลเซียม',
    'iron': 'เหล็ก',
    'potassium': 'โปแตสเซียม',
    'sodium': 'โซเดียม'
}

# ===== Units =====
NUTRITION_UNITS = {
    'calories': 'kcal',
    'protein': 'g',
    'carbs': 'g',
    'fat': 'g',
    'fiber': 'g',
    'vitamin_a': 'µg',
    'vitamin_c': 'mg',
    'vitamin_b1': 'mg',
    'vitamin_b2': 'mg',
    'calcium': 'mg',
    'iron': 'mg',
    'potassium': 'mg',
    'sodium': 'mg'
}

# ===== Unit Conversions (for ingredient parsing) =====
UNIT_CONVERSIONS = {
    'ช้อนโต๊ะ': 15,
    'ช้อนชา': 5,
    'ถ้วย': 200,
    'กลีบ': 5,
    'ผล': 50,
    'หัว': 100,
    'ฟอง': 50,
}