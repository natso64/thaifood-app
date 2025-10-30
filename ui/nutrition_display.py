"""
ui/nutrition_display.py
แสดงผลข้อมูลโภชนาการ
"""

import streamlit as st
from typing import Dict
from utils.constants import THAI_NAMES, NUTRITION_UNITS


def display_nutrition(nutrition_data: Dict, recipe_name: str = ""):
    """แสดงผลโภชนาการอย่างสวยงาม"""
    
    if not nutrition_data or 'total' not in nutrition_data:
        st.warning("ไม่สามารถคำนวณโภชนาการได้")
        return
    
    total = nutrition_data['total']
    total_weight = nutrition_data.get('total_weight', 0)
    
    if recipe_name:
        st.subheader(f"📊 ข้อมูลโภชนาการ: {recipe_name}")
    else:
        st.subheader("📊 ข้อมูลโภชนาการ")
    
    # แสดงส่วนผสมที่ match
    if nutrition_data.get('matched_ingredients'):
        with st.expander("🔍 ส่วนผสมที่ใช้คำนวณ"):
            for item in nutrition_data['matched_ingredients']:
                st.write(f"- {item['name']} ({item['amount']:.0f} g) → {item['matched_db']}")
    
    # สร้าง 2 columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🍽️ โภชนาการรวมทั้งหมด")
        st.markdown(f"**น้ำหนักรวม:** {total_weight:.0f} กรัม")
        
        for nutrient, thai_name in THAI_NAMES.items():
            if nutrient in total:
                value = total[nutrient]
                unit = NUTRITION_UNITS.get(nutrient, '')
                
                emoji = get_nutrient_emoji(nutrient)
                st.metric(
                    label=f"{emoji} {thai_name}",
                    value=f"{value:.1f} {unit}"
                )
    
    with col2:
        st.markdown("### 📏 โภชนาการต่อ 100 กรัม")
        
        if total_weight > 0:
            ratio = 100.0 / total_weight
            
            for nutrient, thai_name in THAI_NAMES.items():
                if nutrient in total:
                    value_per_100g = total[nutrient] * ratio
                    unit = NUTRITION_UNITS.get(nutrient, '')
                    
                    emoji = get_nutrient_emoji(nutrient)
                    st.metric(
                        label=f"{emoji} {thai_name}",
                        value=f"{value_per_100g:.1f} {unit}"
                    )
    
    # แสดงกราฟ Macronutrients
    display_macros_chart(total)


def get_nutrient_emoji(nutrient: str) -> str:
    """คืน emoji สำหรับแต่ละสารอาหาร"""
    emoji_map = {
        'calories': '🔥',
        'protein': '💪',
        'carbs': '⚡',
        'fat': '⚡',
    }
    
    if 'vitamin' in nutrient:
        return '🌟'
    
    return emoji_map.get(nutrient, '💎')


def display_macros_chart(total: Dict):
    """แสดงกราฟสัดส่วน Macronutrients"""
    
    st.markdown("### 📊 สัดส่วนสารอาหารหลัก")
    
    macro_data = {
        'โปรตีน': total.get('protein', 0),
        'คาร์โบไฮเดรต': total.get('carbs', 0),
        'ไขมัน': total.get('fat', 0)
    }
    
    total_macro = sum(macro_data.values())
    
    if total_macro > 0:
        macro_percent = {k: (v/total_macro)*100 for k, v in macro_data.items()}
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("โปรตีน", f"{macro_percent['โปรตีน']:.1f}%")
        with col2:
            st.metric("คาร์โบไฮเดรต", f"{macro_percent['คาร์โบไฮเดรต']:.1f}%")
        with col3:
            st.metric("ไขมัน", f"{macro_percent['ไขมัน']:.1f}%")