import streamlit as st
import pandas as pd
import re

from functions.data import load_food_data
from functions.search import (
    get_name_embeddings, load_model, get_embeddings, get_ingredient_embeddings, search_recipes, SENTENCE_TRANSFORMERS_AVAILABLE, SKLEARN_AVAILABLE
)
from functions.nutrition import SimpleNutritionCalculator
from functions.ui import display_ingredients, display_nutrition_card


# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="Thai Food Reccommender",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load fonts and styles from templates
try:
    with open("templates/fonts.html", "r", encoding="utf-8") as f:
        st.markdown(f.read(), unsafe_allow_html=True)
except Exception:
    pass
try:
    with open("templates/styles.css", "r", encoding="utf-8") as f:
        st.markdown(f"""
<style>
        {f.read()}
</style>
""", unsafe_allow_html=True)
except Exception:
    pass

NUTRITION_PATH = "thai_ingredients_nutrition_data.csv"



# ฟังก์ชันหลัก
def main():
    # โหลดข้อมูลและโมเดลก่อน
    with st.spinner("กำลังโหลดระบบ..."):
        model = load_model()
        data = load_food_data()
        
        if data.empty:
            st.error("ไม่สามารถโหลดข้อมูลอาหารได้")
            return
        
        #embeddings = get_embeddings(model, data)
        name_embeddings = get_name_embeddings(model, data)
        ingredient_embeddings = get_ingredient_embeddings(model, data)
        nutrition_calculator = SimpleNutritionCalculator()
    

    st.markdown(f"""
    <div class="main-header">
        <h1>🍲 ระบบแนะนำรายการอาหารไทย</h1>
        <p>Thai Food Recommendation System</p>
    </div>
    """, unsafe_allow_html=True)
    
    
    # แท็บหลัก
    tab1, tab2 = st.tabs(["🔍 ค้นหาอาหาร", "📋 ข้อมูลทั้งหมด"])
    
    with tab1:
        st.markdown("## ค้นหาสูตรอาหารและวิเคราะห์คุณค่าทางโภชนาการ")
        
        # แสดงเคล็ดลับการค้นหา
        st.markdown("""
        <div class="search-tips">
            <h4>💡 เคล็ดลับการค้นหา:</h4>
            <ul>
                <li><strong>ชื่ออาหาร:</strong> ต้มยำกุ้ง, ผัดไทย, แกงเผ็ด</li>
                <li><strong>วัตถุดิบ:</strong> อาหารที่มีกุ้ง, เมนูไก่</li>
            </ul>
            
        </div>
        """, unsafe_allow_html=True)
        
        # ช่องค้นหา (ใช้ฟอร์มเพื่อให้สามารถกด Enter หรือกดปุ่ม Search)
        with st.form("search_form"):
            query_input = st.text_input(
                "🔍 ค้นหาอาหารที่ต้องการ:",
                placeholder="เช่น ต้มยำกุ้ง, ผัดไทย, อาหารที่มีโปรตีนสูง...",
                help="พิมพ์ชื่ออาหาร วัตถุดิบ หรือคำอธิบายที่เกี่ยวข้อง"
            )

            col_sr, col_sim = st.columns(2)
            with col_sr:
                max_results = st.slider(
                    "จำนวนผลลัพธ์สูงสุด (แสดงผล)",
                    1,
                    max(1, len(data)),
                    min(20, len(data)),
                )
            with col_sim:
                sim_percent = st.slider(
                    "ความคล้ายคลึง (%)",
                    0,
                    100,
                    50,
                )

            submitted = st.form_submit_button("Search")

        # เมื่อฟอร์มถูกส่ง และมีข้อความค้นหา ให้ทำการค้นหา
        if submitted and query_input:
            query = query_input.strip()
            sim_threshold = sim_percent / 100.0

            with st.spinner(f"กำลังค้นหา '{query}'..."):
                effective_query = query

                results = search_recipes(
                    effective_query,
                    model,
                    data,
                    name_embeddings,
                    ingredient_embeddings,
                    max_results,
                    min_similarity=sim_threshold
                )
            
            if results:
                filtered_results = [r for r in results if r.get('similarity', 0) >= sim_threshold]
                st.markdown(f"### 🍽️ พบ {len(filtered_results)} รายการที่เกี่ยวข้อง")
                
                for i, result in enumerate(filtered_results[:max_results], 1):
                    label = f"{i}. {result['name']} (ความเกี่ยวข้อง: {result['similarity']:.1%})"
                    similarity_class = "low-similarity" if result['similarity'] < 0.5 else ""
                    with st.expander(label, icon="▪️"):
                        st.markdown("""
                        <div class="recipe-card">
                            <h4 style="margin-top: 0;">🧾 ข้อมูลอาหาร</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        display_ingredients(result.get('ingredients', ''))

                        st.markdown("### 👨‍🍳 วิธีทำ")
                        method_text = result.get('method', '')
                        if method_text:
                            method_text = method_text.replace('. ', '.\n\n')
                            st.markdown(f"""
                            <div class="recipe-card" style="background: #f8f9fa; border-left: 4px solid #17a2b8;">
                                {method_text}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.info("ไม่มีข้อมูลวิธีทำ")


                        if st.button("แสดงโภชนาการ", key=f"nutri_{result['index']}"):
                            nutrition_data = nutrition_calculator.calculate_recipe_nutrition(
                                result.get('ingredients', '')
                            )
                            display_nutrition_card(nutrition_data)
                        
                        if st.button("แสดงตารางเปรียบเทียบวัตถุดิบกับโภชนาการ", key=f"compare_{result['index']}"):
                            ingredients_text = result.get('ingredients', '')
                            rows = []
                            if ingredients_text:
                                lines = [line.strip() for line in ingredients_text.split('\n') if line.strip()]
                                for line in lines:
                                    clean_line = re.sub(r'^[-•*]\s*', '', line)
                                    if not clean_line:
                                        continue
                                    amount_g = nutrition_calculator.estimate_ingredient_amount(clean_line)
                                    per100 = nutrition_calculator.find_nutrition_match(clean_line)
                                    factor = amount_g / 100.0 if amount_g else 0
                                    rows.append({
                                        'วัตถุดิบ': clean_line,
                                        'ปริมาณ (g)': float(amount_g),
                                        'แคลอรี่ (kcal)': float(per100.get('calories', 0) * factor),
                                        'โปรตีน (g)': float(per100.get('protein', 0) * factor),
                                        'ไขมัน (g)': float(per100.get('fat', 0) * factor),
                                        'คาร์โบไฮเดรต (g)': float(per100.get('carbs', 0) * factor)
                                    })
                            if rows:
                                df_compare = pd.DataFrame(rows)
                                # รวมท้ายตาราง
                                totals = {
                                    'วัตถุดิบ': 'รวมทั้งหมด',
                                    'ปริมาณ (g)': df_compare['ปริมาณ (g)'].sum(),
                                    'แคลอรี่ (kcal)': df_compare['แคลอรี่ (kcal)'].sum(),
                                    'โปรตีน (g)': df_compare['โปรตีน (g)'].sum(),
                                    'ไขมัน (g)': df_compare['ไขมัน (g)'].sum(),
                                    'คาร์โบไฮเดรต (g)': df_compare['คาร์โบไฮเดรต (g)'].sum()
                                }
                                df_compare = pd.concat([df_compare, pd.DataFrame([totals])], ignore_index=True)
                                st.dataframe(df_compare.round(2), use_container_width=True, hide_index=True)
                            else:
                                st.info("ไม่มีข้อมูลวัตถุดิบสำหรับแสดงตาราง")
                
            else:
                st.warning(f"ไม่พบอาหารที่ตรงกับคำค้นหา '{query}'")
                st.info("""
                💡 **เคล็ดลับ:**
                - ลองใช้คำค้นหาที่กว้างขึ้น เช่น 'กุ้ง' แทน 'ต้มยำกุ้ง'
                - ตรวจสอบการสะกดคำ
                """)
    
    with tab2:
        st.markdown("## 📋 ข้อมูลสูตรอาหารทั้งหมด")
        
        # ตัวกรองข้อมูล
        col1, = st.columns(1)
        
        with col1:
            name_filter = st.text_input("🔍 กรองตามชื่อ:", placeholder="พิมพ์ชื่ออาหาร...")
        
        # กรองข้อมูล
        filtered_data = data.copy()
        
        if name_filter:
            filtered_data = filtered_data[
                filtered_data['name'].str.contains(name_filter, case=False, na=False)
            ]
        
        st.markdown(f"**พบ {len(filtered_data)} รายการ** (จากทั้งหมด {len(data)} รายการ)")
        
        # แสดงข้อมูลในตาราง
        if not filtered_data.empty:
            # เพิ่มคอลัมน์ประมาณคุณค่าทางโภชนาการ
            with st.spinner("กำลังคำนวณคุณค่าทางโภชนาการ..."):
                nutrition_summary = []
                for _, row in filtered_data.head(50).iterrows():  # จำกัดแค่ 50 รายการเพื่อความเร็ว
                    nutrition = nutrition_calculator.calculate_recipe_nutrition(
                        row.get('ingredient', ''))
                    nutrition_summary.append(nutrition)
                
                filtered_data_display = filtered_data.head(50).copy()
                filtered_data_display['แคลอรี่ (kcal)'] = [n.get('calories', 0) for n in nutrition_summary]
                filtered_data_display['โปรตีน (g)'] = [n.get('protein', 0) for n in nutrition_summary]
                filtered_data_display['ไขมัน (g)'] = [n.get('fat', 0) for n in nutrition_summary]
                filtered_data_display['คาร์โบไหดเรต (g)'] = [n.get('carbs', 0) for n in nutrition_summary]
            
            # แสดงตาราง
            st.dataframe(
                filtered_data_display[['name', 'แคลอรี่ (kcal)', 'โปรตีน (g)', 'ไขมัน (g)', 'คาร์โบไหดเรต (g)']].round(1),
                use_container_width=True,
                hide_index=True
            )
            
        else:
            st.info("ไม่พบข้อมูลที่ตรงกับเกณฑ์การกรอง")
    
    

if __name__ == "__main__":
    main()