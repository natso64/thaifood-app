# ==============================================================================
# รวมโค้ด Streamlit App
# เวอร์ชันบังคับ: ใช้ sentence-transformers และ sklearn cosine_similarity เท่านั้น
# ==============================================================================

# --- (1) Imports ---
import streamlit as st
import pandas as pd
import os
import re
import pickle
import numpy as np
from typing import Dict, List, Any, Tuple

# Imports สำหรับ AI/ML (Sentence Transformers และ Sklearn)
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- (2) ฝังเนื้อหา CSS และ HTML ---

# โหลด Google Fonts (Sarabun)
FONTS_HTML = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif !important; }
</style>
"""

# CSS Stylesheet หลักสำหรับ App
STYLES_CSS = """
.main-header {
    background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.recipe-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: transform 0.2s, box-shadow 0.2s;
}
.recipe-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* --- ส่วนหัวผลลัพธ์ --- */
.section-header {
    background: linear-gradient(90deg, #667eea, #764ba2);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    margin: 1.5rem 0 1rem 0;
    font-size: 1.3rem;
    font-weight: 600;
}

/* --- สไตล์การแสดงวัตถุดิบ --- */
.ingredient-group-header {
    font-weight: 600;
    color: #4ecdc4;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    border-bottom: 2px solid #f0f0f0;
    padding-bottom: 4px;
}
.ingredient-list {
    background: #f8f9fa;
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 5px;
}
.ingredient-item {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    border-bottom: 1px dashed #ddd;
}
.ingredient-item:last-child {
    border-bottom: none;
}
.ingredient-name {
    font-weight: 500;
}
.ingredient-quantity {
    color: #555;
    font-size: 0.95rem;
    text-align: right;
    white-space: nowrap;
    padding-left: 1rem;
}

/* --- สไตล์โภชนาการ --- */
.nutrition-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
    padding: 1.5rem;
    color: white;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.nutrition-card h3 {
    color: white;
    margin-top: 0;
    margin-bottom: 1rem;
}
.nutrition-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 0.8rem;
}
.nutrition-metric {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    padding: 0.8rem;
    border-radius: 8px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.2);
}
.nutrition-metric h5 {
    color: #fff;
    margin: 0;
    font-size: 1.4rem;
    font-weight: 700;
}
.nutrition-metric p {
    margin: 0.3rem 0 0 0;
    font-size: 0.85rem;
    color: rgba(255,255,255,0.9);
}

/* --- สไตล์วิธีทำแบบใหม่ (มีขั้นตอน) --- */
.method-grid {
    display: grid;
    grid-template-columns: auto 1fr; /* Column 1 for number, Column 2 for text */
    gap: 0px 20px; /* No row gap, 20px column gap */
    padding: 10px;
    border-radius: 10px;
    background-color: rgba(240, 242, 246, 0.7);
    margin-bottom: 20px;
}

.method-step {
    display: contents; /* Important for grid alignment */
}

.step-number {
    font-weight: bold;
    padding: 8px 0;
    border-bottom: 1px solid #e0e0e0;
    text-align: left;
}

.step-description {
    padding: 8px 0;
    border-bottom: 1px solid #e0e0e0;
    text-align: left;
}

.method-step:last-child .step-number,
.method-step:last-child .step-description {
    border-bottom: none;
}

.method-subheading {
    grid-column: 1 / -1; /* Make the subheading span across all columns */
    font-weight: bold;
    color: #4B4B4B; /* A slightly darker color for emphasis */
    padding-top: 15px; /* Add space above the subheading */
    padding-bottom: 5px; /* Add space below the subheading */
    border-bottom: 2px solid #D0D0D0; /* A stronger border */
    margin-bottom: 5px; /* Space before the first step of this group */
}

.data-grid {
    display: block;
    padding: 15px;
    border-radius: 10px;
    background-color: rgba(240, 242, 246, 0.8);
    margin-bottom: 20px;
}

.data-grid > div {
    padding: 8px 5px;
    border-bottom: 1px solid #e0e0e0;
    text-align: left;
}

.grid-subheading {
    font-weight: bold;
    color: #333;
    border-bottom: 1.5px solid #ccc;
    margin-top: 10px;
}
.grid-inline-note strong {
    font-weight: bold;
    color: #333;
    margin-top: 10px;
}

.data-grid > div:last-child {
    border-bottom: none;
}

.search-tips {
    background-color: #e6f7ff;
    border: 1px solid #b3e0ff;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 20px;
}
.search-tips h4 { color: #0056b3; margin-top: 0; }
.search-tips ul { padding-left: 20px; }

/* --- สไตล์ Tabs --- */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    background-color: #f0f2f6;
    border-radius: 8px 8px 0 0;
    padding: 0 24px;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background-color: #667eea;
    color: white;
}

/* --- การ์ดโภชนาการแบบที่ 2  --- */
.nutrition-card-pink {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    
}
"""

# --- (3) ฟังก์ชันโหลดและเตรียมข้อมูล ---

RECIPES_PATH = "data/recipes.csv"
INGREDIENTS_PATH = "data/ingredients.csv"
NUTRITION_DATA_PATH = "data/thai_ingredients_nutrition.csv"

@st.cache_data
def load_and_preprocess_data():
    """โหลดข้อมูลจาก recipes.csv และ ingredients.csv"""
    if not os.path.exists(RECIPES_PATH) or not os.path.exists(INGREDIENTS_PATH):
        st.error(f"ไม่พบไฟล์ {RECIPES_PATH} หรือ {INGREDIENTS_PATH}")
        return pd.DataFrame(), pd.DataFrame()

    try:
        recipes_df = pd.read_csv(RECIPES_PATH)
        ingredients_df = pd.read_csv(INGREDIENTS_PATH)
    except Exception as e:
        st.error(f"ไม่สามารถอ่านไฟล์ CSV: {e}")
        return pd.DataFrame(), pd.DataFrame()

    if 'recipe_id' not in recipes_df.columns or 'recipe_name' not in recipes_df.columns:
        st.error("ไฟล์ recipes.csv ต้องมีคอลัมน์ 'recipe_id' และ 'recipe_name'")
        return pd.DataFrame(), pd.DataFrame()
        
    if 'recipe_id' not in ingredients_df.columns or 'ingredient_name' not in ingredients_df.columns:
        st.error("ไฟล์ ingredients.csv ต้องมีคอลัมน์ 'recipe_id' และ 'ingredient_name'")
        return pd.DataFrame(), pd.DataFrame()

    ingredients_df['ingredient_name'] = ingredients_df['ingredient_name'].fillna('').astype(str)
    
    # รวมวัตถุดิบทั้งหมดของแต่ละ recipe_id ให้เป็น text ก้อนเดียว
    ingredient_text_grouped = ingredients_df.groupby('recipe_id')['ingredient_name'].apply(
        lambda x: ' '.join(x.unique())
    )
    
    ingredient_text_df = ingredient_text_grouped.reset_index()
    ingredient_text_df.columns = ['recipe_id', 'ingredient_text']

    # รวมตารางหลัก (recipes) เข้ากับตารางวัตถุดิบ (ingredient_text)
    main_df = pd.merge(recipes_df, ingredient_text_df, on='recipe_id', how='left')
    main_df['ingredient_text'] = main_df['ingredient_text'].fillna('')
    
    st.success("โหลดข้อมูลสำเร็จ")
    return main_df, ingredients_df

@st.cache_data
def load_nutrition_data() -> (Dict[str, Any], List[str]):
    """โหลดข้อมูลโภชนาการจาก thai_ingredients_nutrition.csv"""
    if not os.path.exists(NUTRITION_DATA_PATH):
        st.warning(f"ไม่พบไฟล์ข้อมูลโภชนาการ: {NUTRITION_DATA_PATH}")
        return {}, []
    
    try:
        df = pd.read_csv(NUTRITION_DATA_PATH)
        if 'ingredient' not in df.columns or 'calories' not in df.columns:
            st.error("ไฟล์โภชนาการขาดคอลัมน์ที่จำเป็น")
            return {}, []
        
        # แปลงเป็น dict (map) เพื่อให้ค้นหาข้อมูลโภชนาการได้เร็ว
        nutrition_map = {row['ingredient'].strip(): row for _, row in df.iterrows()}
        keys = list(nutrition_map.keys())
        keys.sort(key=len, reverse=True)
        
        return nutrition_map, keys
    except Exception as e:
        st.error(f"ไม่สามารถโหลดไฟล์โภชนาการ: {e}")
        return {}, []

# --- (4) ฟังก์ชันแสดงผล UI (Widgets) ---

def display_ingredients(recipe_id: int, ingredients_df: pd.DataFrame):
    """แสดงผลวัตถุดิบจาก DataFrame โดยจัดกลุ่มตาม component_group"""
    
    recipe_ingredients = ingredients_df[ingredients_df['recipe_id'] == recipe_id].copy()
    
    if recipe_ingredients.empty:
        st.info("ไม่พบข้อมูลวัตถุดิบสำหรับสูตรนี้")
        return

    recipe_ingredients['component_group'] = recipe_ingredients['component_group'].fillna('ส่วนผสม')
    grouped = recipe_ingredients.groupby('component_group')
    
    html_output = ""
    
    for group_name, group_df in sorted(grouped, key=lambda x: x[0]):
        html_output += f"<h4 class='ingredient-group-header'>{group_name}</h4>"
        html_output += "<div class='ingredient-list'>"
        
        for _, row in group_df.iterrows():
            name = row.get('ingredient_name', 'N/A')
            quantity = row.get('quantity', '')
            unit = row.get('unit', '')

            quantity_str = str(quantity) if pd.notna(quantity) else ""
            unit_str = str(unit) if pd.notna(unit) else ""
            full_quantity = f"{quantity_str} {unit_str}".strip()

            html_output += "<div class='ingredient-item'>"
            html_output += f"<span class='ingredient-name'>• {name}</span>"
            if full_quantity:
                html_output += f"<span class='ingredient-quantity'>{full_quantity}</span>"
            html_output += "</div>"
        
        html_output += "</div>"

    st.markdown(html_output, unsafe_allow_html=True)

def calculate_nutrition(
    recipe_id: int, 
    ingredients_df: pd.DataFrame, 
    nutrition_map: Dict[str, Any]
) -> (Dict[str, float], List[str]):
    """ประมาณการค่าโภชนาการจาก recipe_id (รองรับคอลัมน์เพิ่มเติม)"""
    if ingredients_df.empty or not nutrition_map:
        return {}, []
    
    recipe_ingredients = ingredients_df[ingredients_df['recipe_id'] == recipe_id]
    
    if recipe_ingredients.empty:
        return {}, []

    # คอลัมน์โภชนาการทั้งหมด
    totals = {
        'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0,
        'fiber': 0, 'vitamin_a': 0, 'vitamin_c': 0,
        'vitamin_b1': 0, 'vitamin_b2': 0,
        'calcium': 0, 'iron': 0, 'potassium': 0, 'sodium': 0
    }
    found_ingredients = set()

    for _, row in recipe_ingredients.iterrows():
        # ใช้ nutrition_name ถ้ามี, ถ้าไม่มี ใช้ ingredient_name
        match_key = row.get('nutrition_name')
        if pd.isna(match_key):
            match_key = row.get('ingredient_name')
        if pd.isna(match_key):
            continue
            
        match_key = str(match_key).strip()

        # ตรวจสอบว่าวัตถุดิบนี้มีในฐานข้อมูลโภชนาการหรือไม่
        if match_key in nutrition_map:
            row_data = nutrition_map[match_key]
            
            for key in totals.keys():
                totals[key] += row_data.get(key, 0)
            
            found_ingredients.add(match_key)

    return totals, list(found_ingredients)

# --- ฟังก์ชันคำนวณและแสดงผลโภชนาการ ---

def calculate_nutrition_per_100g(
    totals: Dict[str, float],
    total_weight_grams: float = 500.0  # สมมติน้ำหนักเริ่มต้น 500g
) -> Dict[str, float]:
    """
    คำนวณโภชนาการต่อ 100 กรัม
    """
    if total_weight_grams <= 0:
        return totals.copy()
    
    per_100g = {}
    for key, value in totals.items():
        per_100g[key] = (value / total_weight_grams) * 100
    
    return per_100g

def display_nutrition_card(
    totals: Dict[str, float], 
    title: str = "โภชนาการทั้งหมด",
    gradient_colors: tuple = ("#667eea", "#667eea")
):
    """แสดงการ์ดโภชนาการ (ใช้ซ้ำได้) พร้อมหน่วยที่ถูกต้อง"""
    
    if not totals or totals.get('calories', 0) == 0:
        st.info("ไม่สามารถคำนวณโภชนาการได้")
        return

    st.markdown(f"""
    <div class="nutrition-card" style="background: linear-gradient(135deg, {gradient_colors[0]} 0%, {gradient_colors[1]} 100%);">
        <h3>{title}</h3>
        <div class="nutrition-grid">
            <div class="nutrition-metric">
                <h5>{totals.get('calories', 0):.0f}</h5>
                <p>แคลอรี (kcal)</p>
            </div>
            <div class="nutrition-metric">
                <h5>{totals.get('protein', 0):.2f}</h5>
                <p>โปรตีน (g)</p>
            </div>
            <div class="nutrition-metric">
                <h5>{totals.get('carbs', 0):.2f}</h5>
                <p>คาร์โบไฮเดรต (g)</p>
            </div>
            <div class="nutrition-metric">
                <h5>{totals.get('fat', 0):.2f}</h5>
                <p>ไขมัน (g)</p>
            </div>
            <div class="nutrition-metric">
                <h5>{totals.get('fiber', 0):.2f}</h5>
                <p>ใยอาหาร (g)</p>
            </div>
            <div class="nutrition-metric">
                <h5>{totals.get('vitamin_a', 0):.2f}</h5>
                <p>วิตามิน A (mcg)</p>
            </div>
            <div class="nutrition-metric">
                <h5>{totals.get('vitamin_c', 0):.2f}</h5>
                <p>วิตามิน C (mg)</p>
            </div>
            <div class="nutrition-metric">
                <h5>{totals.get('vitamin_b1', 0):.2f}</h5>
                <p>วิตามิน B1 (mg)</p>
            </div>
            <div class="nutrition-metric">
                <h5>{totals.get('vitamin_b2', 0):.2f}</h5>
                <p>วิตามิน B2 (mg)</p>
            </div>
            <div class="nutrition-metric">
                <h5>{totals.get('calcium', 0):.2f}</h5>
                <p>แคลเซียม (mg)</p>
            </div>
            <div class="nutrition-metric">
                <h5>{totals.get('iron', 0):.2f}</h5>
                <p>เหล็ก (mg)</p>
            </div>
            <div class="nutrition-metric">
                <h5>{totals.get('potassium', 0):.2f}</h5>
                <p>โพแทสเซียม (mg)</p>
            </div>
            <div class="nutrition-metric">
                <h5>{totals.get('sodium', 0):.2f}</h5>
                <p>โซเดียม (mg)</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def calculate_total_weight(
    recipe_id: int,
    ingredients_df: pd.DataFrame
) -> float:
    """
    คำนวณน้ำหนักรวมของวัตถุดิบ (กรัม)
    Returns:
        น้ำหนักรวม (กรัม) หรือ 500 ถ้าคำนวณไม่ได้
    """
    if ingredients_df.empty:
        return 500.0
    
    recipe_ingredients = ingredients_df[ingredients_df['recipe_id'] == recipe_id]
    
    if recipe_ingredients.empty:
        return 500.0
    
    total_weight = 0.0
    
    for _, row in recipe_ingredients.iterrows():
        quantity = row.get('quantity', 0)
        unit = row.get('unit', '')
        
        if pd.notna(quantity) and pd.notna(unit):
            try:
                quantity = float(quantity)
                unit = str(unit).lower().strip()
                
                # แปลงหน่วยเป็นกรัม
                if unit in ['กรัม', 'g', 'gram', 'กก.']:
                    if unit == 'กก.':
                        total_weight += quantity * 1000
                    else:
                        total_weight += quantity
                elif unit in ['มล.', 'ml', 'cc']:
                    total_weight += quantity  # สมมติความหนาแน่น 1 g/ml
                elif unit in ['ช้อนโต๊ะ', 'tablespoon', 'tbsp']:
                    total_weight += quantity * 15  # 1 ช้อนโต๊ะ ≈ 15g
                elif unit in ['ช้อนชา', 'teaspoon', 'tsp']:
                    total_weight += quantity * 5   # 1 ช้อนชา ≈ 5g
                elif unit in ['ถ้วย', 'cup']:
                    total_weight += quantity * 240  # 1 ถ้วย ≈ 240g
                elif unit in ['ใบ', 'leaf', 'กิ่ง']:
                    total_weight += quantity * 2   # สมมติ 1 ใบ/กิ่ง ≈ 2g
                elif unit in ['หัว', 'clove', 'ลูก']:
                    total_weight += quantity * 10  # สมมติ 1 หัว ≈ 10g
            except:
                continue
    
    # ถ้าคำนวณไม่ได้ ให้ใช้ค่าเริ่มต้น
    return total_weight if total_weight > 0 else 500.0

def display_recipe_result(
    idx: int,
    result: Dict[str, Any],
    ingredients_data: pd.DataFrame,
    nutrition_map: Dict[str, Any]
):
    """แสดงผลสูตรอาหาร 1 รายการ (แบบ 2 Tabs)"""
    
    recipe_id = result['recipe_id']
    recipe_name = result['name']
    recipe_method = result.get('method', '')
    
    
    st.markdown(f"---")
    st.markdown(f"""
    <div class="recipe-card">
        <h3>{idx}. {recipe_name}</h3>
        <p>(ความคล้าย: {result.get('similarity', 0)*100:.2f}%)</p>
    </div>
    """, unsafe_allow_html=True)

    # สร้าง 2 Tabs
    tab1, tab2 = st.tabs(["📋 วัตถุดิบและวิธีทำ", "📊 ข้อมูลโภชนาการ"])
    
    # Tab 1: วัตถุดิบและวิธีทำ
    with tab1:
        col1, col2 = st.columns([1, 1.2])
        
        with col1:
            st.markdown("### 🥘 วัตถุดิบ")
            display_ingredients(recipe_id, ingredients_data)
        
        with col2:
            st.markdown("### 🍳 วิธีทำ")
            display_method(recipe_method)
    
    # Tab 2: โภชนาการ
    with tab2:
        if (ingredients_data is not None 
            and not ingredients_data.empty 
            and nutrition_map):
            
            # คำนวณโภชนาการ
            totals, found = calculate_nutrition(
                recipe_id, 
                ingredients_data, 
                nutrition_map
            )
            
            # คำนวณน้ำหนักรวม
            total_weight = calculate_total_weight(recipe_id, ingredients_data)
            
            # คำนวณโภชนาการต่อ 100g
            per_100g = calculate_nutrition_per_100g(totals, total_weight)
            
            # แสดงผลแบบ 2 คอลัมน์
            col1, col2 = st.columns(2)
            
            with col1:
                display_nutrition_card(
                    totals, 
                    title=f"📊 โภชนาการทั้งหมด",
                    gradient_colors=("#667eea", "#764ba2")
                )
            
            with col2:
                display_nutrition_card(
                    per_100g, 
                    title="📊 โภชนาการต่อ 100 กรัม",
                    gradient_colors=("#f093fb", "#f5576c")
                )
            
        else:
            st.info("ไม่สามารถคำนวณโภชนาการได้")


def display_method(recipe_method: str):
    """
    แสดงวิธีทำและจัดการ 'หมายเหตุ' ได้อย่างถูกต้องและมีสไตล์
    """

    if not recipe_method or not recipe_method.strip():
        st.warning("ไม่พบข้อมูลวิธีทำ")
        return
    
    full_text = recipe_method.strip()
    lines = [line.strip() for line in full_text.split('\n') if line.strip()]
    method_lines = []
    
    # แยก "หมายเหตุ" ส่วนท้ายเรื่องออกมาก่อน
    for line in lines:
        method_lines.append(line)
    method_steps_text = "\n".join(method_lines)
    

    # --- สร้าง HTML สำหรับ "ขั้นตอนวิธีทำ" ---
    if method_steps_text:
        step_lines = [line.strip() for line in method_steps_text.split('\n') if line.strip()]
        
        if step_lines:
            html_output = '<div class="data-grid">'
            step_counter = 1

            for line in step_lines:
                
                # หัวข้อย่อย คือ บรรทัดที่ลงท้ายด้วย : หรือขึ้นต้นด้วย ##
                is_subheading = (line.endswith(':') or line.startswith('##')) and not re.match(r'^\d+\.\s*', line)
                is_subheading_note_inline = re.match(r'^\*\*(.+?)\*\* (.+)', line.strip())
                is_subheading_note_step = re.match(r'^\*\*(.+?)\*\*$', line.strip())

                if is_subheading:
                    subheading_text = line.replace('##', '').replace(':', '').strip()
                    html_output += f'<div class="grid-subheading">{subheading_text}</div>'
                    step_counter = 1
                
                elif is_subheading_note_inline:
                    header_text = is_subheading_note_inline.group(1).strip()
                    desc_text = is_subheading_note_inline.group(2).strip()
                    html_output += f'<div class="grid-inline-note">📝 <strong>{header_text}</strong> <span>{desc_text}</span></div>'

                # หมายเหตุ ที่แทรกในขั้นตอน
                elif is_subheading_note_step:
                    header_text = is_subheading_note_step.group(1).strip()
                    html_output += f'<div class="grid-subheading">📝 {header_text}</div>'
                    step_counter = 1

                # ขั้นตอนปกติ
                else:
                    description = re.sub(r'^\s*\d+\.\s*', '', line).strip()
                    html_output += f'<div>{step_counter}. {description}</div>'
                    step_counter += 1

            html_output += '</div>'
            st.markdown(html_output, unsafe_allow_html=True)
            

# --- (5) ฟังก์ชันการค้นหา (AI/ML) ---

EMBEDDINGS_NAME_PATH = 'embeddings_name.pkl'
EMBEDDINGS_INGREDIENT_PATH = 'embeddings_ingredient.pkl'
MODEL_PATH = "model"
# บังคับใช้โมเดลนี้เท่านั้น
MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'

@st.cache_resource
def load_model():
    """โหลดโมเดล SentenceTransformer (จาก local หรือ download)"""
    
    # 1. พยายามโหลดจาก local (ถ้าเคยโหลดมาแล้ว)
    if os.path.exists(MODEL_PATH):
        try:
            return SentenceTransformer(MODEL_PATH)
        except Exception as e:
            st.warning(f"ไม่สามารถโหลดโมเดลจาก {MODEL_PATH}: {e}")

    # 2. ถ้าโหลด local ไม่ได้ ให้ดาวน์โหลดจาก Hugging Face
    try:
        with st.spinner(f"กำลังดาวน์โหลดโมเดลการค้นหา..."):
            model = SentenceTransformer(MODEL_NAME)
            os.makedirs(MODEL_PATH, exist_ok=True)
            model.save(MODEL_PATH)
        return model
    except Exception as e:
        st.error(f"ไม่สามารถดาวน์โหลดโมเดล: {e}")
        return None

@st.cache_data
def get_name_embeddings(_model, data):
    """สร้างหรือโหลด Name Embeddings"""
    
    # 1. พยายามโหลด embeddings ที่คำนวณไว้แล้วจากไฟล์ .pkl
    if os.path.exists(EMBEDDINGS_NAME_PATH):
        try:
            with open(EMBEDDINGS_NAME_PATH, 'rb') as f:
                return pickle.load(f)
        except Exception:
            pass 
    
    if data.empty:
        return np.array([])
        
    texts = data['recipe_name'].fillna('').astype(str).tolist()
    
    # 2. ถ้าไม่มีไฟล์ .pkl ให้สร้าง embeddings ใหม่
    with st.spinner("กำลังสร้างดัชนีการค้นหา (ชื่ออาหาร)..."):
        # _model.encode จะล้มเหลวหาก _model เป็น None (ซึ่งเป็นพฤติกรรมที่คาดหวัง)
        embeddings = _model.encode(texts) 
    
    # 3. บันทึกไฟล์ .pkl เพื่อใช้ครั้งถัดไป
    try:
        with open(EMBEDDINGS_NAME_PATH, 'wb') as f:
            pickle.dump(embeddings, f)
    except Exception:
        pass
        
    return embeddings

@st.cache_data
def get_ingredient_embeddings(_model, data):
    """สร้างหรือโหลด Ingredient Embeddings"""
    
    # 1. พยายามโหลด embeddings ที่คำนวณไว้แล้วจากไฟล์ .pkl
    if os.path.exists(EMBEDDINGS_INGREDIENT_PATH):
        try:
            with open(EMBEDDINGS_INGREDIENT_PATH, 'rb') as f:
                return pickle.load(f)
        except Exception:
            pass
    
    if data.empty:
        return np.array([])
        
    texts = data['ingredient_text'].fillna('').astype(str).tolist()
    
    # 2. ถ้าไม่มีไฟล์ .pkl ให้สร้าง embeddings ใหม่
    with st.spinner("กำลังสร้างดัชนีการค้นหา (ส่วนผสม)..."):
        embeddings = _model.encode(texts)
    
    # 3. บันทึกไฟล์ .pkl เพื่อใช้ครั้งถัดไป
    try:
        with open(EMBEDDINGS_INGREDIENT_PATH, 'wb') as f:
            pickle.dump(embeddings, f)
    except Exception:
        pass
        
    return embeddings

def parse_search_query(query: str) -> Tuple[str, List[str]]:
    """
    แยกคำค้นหาออกเป็น ชื่อเมนู และ วัตถุดิบ
    รองรับรูปแบบ:
    - "กะเพราหมูสับ" -> ชื่อเมนู
    - "ใบมะกรูด เนื้อหมู ไก่" -> วัตถุดิบ (คั่นด้วยช่องว่าง)
    - "ใบมะกรูด, เนื้อหมู, ไก่" -> วัตถุดิบ (คั่นด้วยจุลภาค)
    """
    query = query.strip()
    
    if ',' in query:
        # ถ้ามีจุลภาค, ถือเป็นรายการวัตถุดิบ
        ingredients = [ing.strip() for ing in query.split(',') if ing.strip()]
        return "", ingredients
    
    words = query.split()
    
    # ถ้ามีมากกว่า 2 คำ, ถือเป็นรายการวัตถุดิบ (คั่นด้วย space)
    if len(words) > 2:
        return "", words
    
    # ถ้าไม่เข้าเงื่อนไข, ถือว่าเป็นชื่อเมนู
    return query, []

def search_recipes(
    query: str, 
    data: pd.DataFrame,
    ingredients_df: pd.DataFrame,
    model: Any, 
    name_embeddings: np.ndarray, 
    ingredient_embeddings: np.ndarray, 
    top_k=10, 
    min_similarity=0.55
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    ค้นหาสูตรอาหาร คืนค่า 2 ลิสต์:
    1. exact_matches: ตรงกัน 100%
    2. similar_matches: คล้ายกัน
    """
    
    if data.empty:
        return [], []
    
    # 1. แยกคำค้นหา (อาจเป็นชื่อเมนู หรือ รายการวัตถุดิบ)
    menu_name, ingredient_list = parse_search_query(query)
    
    exact_matches: List[Dict[str, Any]] = []
    similar_matches: List[Dict[str, Any]] = []
    
    # 2. ค้นหาแบบ Exact Match 100%
    if menu_name:
        # 2.1 ค้นหาชื่อเมนูที่ตรงกัน (case-insensitive)
        exact_name_matches = data[
            data['recipe_name'].str.lower() == menu_name.lower()
        ]
        
        for idx, row in exact_name_matches.iterrows():
            exact_matches.append({
                'recipe_id': int(row['recipe_id']),
                'name': row['recipe_name'],
                'similarity': 1.0,
                'method': row.get('method', ''),
                'index': idx
            })
    
    if ingredient_list:
        # 2.2 ค้นหาเมนูที่มีวัตถุดิบครบทุกชนิด
        for idx, row in data.iterrows():
            ingredient_text = row.get('ingredient_text', '').lower()
            
            if all(ing.lower() in ingredient_text for ing in ingredient_list):
                # ตรวจว่าเจอแล้วหรือยัง (ป้องกันซ้ำ)
                if not any(m['recipe_id'] == row['recipe_id'] for m in exact_matches):
                    exact_matches.append({
                        'recipe_id': int(row['recipe_id']),
                        'name': row['recipe_name'],
                        'similarity': 1.0,
                        'method': row.get('method', ''),
                        'index': idx
                    })
    
    # 3. ค้นหาแบบคล้ายกัน (Semantic Search)
    
    # สร้าง embedding สำหรับคำค้นหา
    query_embedding = model.encode([query])

    # 3.1 ค้นหาจาก "ชื่อเมนู" ที่คล้ายกัน
    if len(name_embeddings) > 0:
        name_similarities = cosine_similarity(query_embedding, name_embeddings)[0]
        top_indices = np.argsort(-name_similarities)[:top_k * 2]
        
        exact_recipe_ids = {m['recipe_id'] for m in exact_matches}
        
        for idx in top_indices:
            if idx < len(data) and name_similarities[idx] >= min_similarity:
                recipe_id = int(data.iloc[idx]['recipe_id'])
                
                # ข้ามถ้าเจอใน exact_matches แล้ว
                if recipe_id not in exact_recipe_ids:
                    similar_matches.append({
                        'recipe_id': recipe_id,
                        'name': data.iloc[idx]['recipe_name'],
                        'similarity': float(name_similarities[idx]),
                        'method': data.iloc[idx].get('method', ''),
                        'index': int(idx)
                    })
    
    # 3.2 ค้นหาจาก "วัตถุดิบ" ที่คล้ายกัน
    if len(ingredient_embeddings) > 0:
        # (ใช้ query_embedding เดียวกันสำหรับค้นหาวัตถุดิบ)
        ingredient_similarities = cosine_similarity(query_embedding, ingredient_embeddings)[0]
        top_indices = np.argsort(-ingredient_similarities)[:top_k * 2]
        
        exact_recipe_ids = {m['recipe_id'] for m in exact_matches}
        similar_recipe_ids = {m['recipe_id'] for m in similar_matches}
        
        for idx in top_indices:
            if idx < len(data) and ingredient_similarities[idx] >= min_similarity:
                recipe_id = int(data.iloc[idx]['recipe_id'])
                
                # ข้ามถ้าเจอใน exact_matches หรือ similar_matches (จากชื่อ) แล้ว
                if recipe_id not in exact_recipe_ids and recipe_id not in similar_recipe_ids:
                    similar_matches.append({
                        'recipe_id': recipe_id,
                        'name': data.iloc[idx]['recipe_name'],
                        'similarity': float(ingredient_similarities[idx]),
                        'method': data.iloc[idx].get('method', ''),
                        'index': int(idx)
                    })
    
    # 4. เรียงลำดับและคืนค่า
    exact_matches = sorted(exact_matches, key=lambda x: x['similarity'], reverse=True)
    similar_matches = sorted(similar_matches, key=lambda x: x['similarity'], reverse=True)
    
    return exact_matches[:top_k], similar_matches[:top_k]

# --- (6) ส่วนหลักของ Streamlit App (Main) ---

st.set_page_config(
    page_title="Thai Food Recommender",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    
    st.markdown(FONTS_HTML, unsafe_allow_html=True)
    st.markdown(f"<style>{STYLES_CSS}</style>", unsafe_allow_html=True)

    with st.spinner("กำลังโหลดระบบ..."):
        model = load_model()
        data, ingredients_data = load_and_preprocess_data()
        nutrition_map, _ = load_nutrition_data()
        
        if data.empty:
            st.error("ไม่สามารถโหลดข้อมูลอาหารได้")
            return
        
        # หาก model โหลดไม่สำเร็จ (เป็น None)
        # 2 บรรทัดนี้จะ raise Exception ซึ่งถูกต้องตามที่คาดหวัง
        # เพราะเราบังคับให้ใช้โมเดลเท่านั้น
        name_embeddings = get_name_embeddings(model, data)
        ingredient_embeddings = get_ingredient_embeddings(model, data)
    
    st.markdown(f"""
    <div class="main-header">
        <h1>🍲 ระบบแนะนำรายการอาหารไทย</h1>
        <p>Thai Food Recommendation System</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔍 ค้นหาอาหาร", "📋 ข้อมูลทั้งหมด"])
    
    # ========================================
    # Tab 1: ค้นหา
    # ========================================
    with tab1:
        st.markdown("## ค้นหาสูตรอาหาร")
        
        st.markdown("""
        <div class="search-tips">
            <h4>💡 เคล็ดลับการค้นหา:</h4>
            <ul>
                <li><strong>ชื่อเมนูเดี่ยว:</strong> กะเพราหมูสับ, ต้มยำกุ้ง, ผัดไทย</li>
                <li><strong>วัตถุดิบ (คั่นด้วยช่องว่าง):</strong> ใบมะกรูด เนื้อหมู ไก่ ไข่เป็ด</li>
                <li><strong>วัตถุดิบ (คั่นด้วยจุลภาค):</strong> ใบมะกรูด, เนื้อหมู, ไก่, ไข่เป็ด</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("search_form"):
            query_input = st.text_input(
                "🔍 ค้นหาอาหารที่ต้องการ:",
                placeholder="เช่น กะเพราหมูสับ, ใบมะกรูด เนื้อหมู, ใบมะกรูด, เนื้อหมู, ไก่...",
                help="พิมพ์ชื่อเมนู หรือ วัตถุดิบ (คั่นด้วยช่องว่างหรือจุลภาค)"
            )

            col_sr, col_sim = st.columns(2)
            with col_sr:
                max_results = st.slider(
                    "จำนวนผลลัพธ์สูงสุด (แต่ละส่วน)",
                    1,
                    max(1, len(data)),
                    min(10, max(1, len(data))),
                )
            with col_sim:
                sim_percent = st.slider(
                    "ความคล้ายคลึงขั้นต่ำ (%) สำหรับส่วนคล้ายกัน",
                    0,
                    100,
                    55,
                )

            submitted = st.form_submit_button("ค้นหา")

        if submitted and query_input:
            min_sim_float = sim_percent / 100.0
            
            with st.spinner(f"กำลังค้นหา \"{query_input}\"..."):
                exact_matches, similar_matches = search_recipes(
                    query=query_input,
                    data=data,
                    ingredients_df=ingredients_data,
                    model=model,
                    name_embeddings=name_embeddings,
                    ingredient_embeddings=ingredient_embeddings,
                    top_k=max_results,
                    min_similarity=min_sim_float
                )
            
            # กรองผลลัพธ์ส่วนคล้ายกัน
            similar_matches = [m for m in similar_matches if m['similarity'] >= min_sim_float]
            
            total_results = len(exact_matches) + len(similar_matches)
            st.markdown(f"## ผลการค้นหา \"{query_input}\" (พบ {total_results} รายการ)")

            if total_results == 0:
                st.warning("ไม่พบสูตรอาหารที่ตรงกับคำค้นหา")
            
            # --- แสดงผลส่วนที่ตรงกัน 100% ---
            if exact_matches:
                st.markdown(f"""
                <div class="section-header">
                    🎯 ตรงกัน 100% ({len(exact_matches)} รายการ)
                </div>
                """, unsafe_allow_html=True)
                
                for idx, result in enumerate(exact_matches):
                    display_recipe_result(
                        idx + 1, 
                        result, 
                        ingredients_data, 
                        nutrition_map
                    )
            
            # --- แสดงผลส่วนที่คล้ายกัน ---
            if similar_matches:
                st.markdown(f"""
                <div class="section-header">
                    🔍 คล้ายกัน ({len(similar_matches)} รายการ)
                </div>
                """, unsafe_allow_html=True)
                
                for idx, result in enumerate(similar_matches):
                    display_recipe_result(
                        idx + 1,
                        result, 
                        ingredients_data, 
                        nutrition_map
                    )

        elif submitted and not query_input:
            st.error("กรุณาป้อนคำค้นหา")

    # ========================================
    # Tab 2: ข้อมูลทั้งหมด
    # ========================================
    with tab2:
        st.markdown("## 📋 ข้อมูลอาหารทั้งหมดในระบบ")
        
        search_all = st.text_input("กรองข้อมูล (พิมพ์ชื่ออาหาร):", key="search_all")
        
        if search_all:
            filtered_data = data[data['recipe_name'].str.contains(search_all, case=False, na=False)].copy()
        else:
            filtered_data = data.copy()

        st.markdown(f"**แสดงผล {len(filtered_data)} รายการ** (จากทั้งหมด {len(data)} รายการ)")
        
        if not filtered_data.empty:
            st.dataframe(
                filtered_data[['recipe_name', 'method', 'ingredient_text']],
                column_config={
                    "recipe_name": "ชื่ออาหาร",
                    "method": "วิธีทำ",
                    "ingredient_text": "วัตถุดิบ (สำหรับค้นหา)"
                },
                use_container_width=True,
                height=500
            )
        else:
            st.info("ไม่พบข้อมูลที่ตรงกับการกรอง")


            
if __name__ == "__main__":
    main()