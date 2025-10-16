import streamlit as st
import pandas as pd
import numpy as np
import os
import re
from typing import Dict
from datetime import datetime

from functions.data import load_food_data
from functions.search import (
    load_model, get_embeddings, get_ingredient_embeddings, search_recipes, SENTENCE_TRANSFORMERS_AVAILABLE, SKLEARN_AVAILABLE
)
from functions.nutrition import SimpleNutritionCalculator
from functions.ui import display_ingredients, display_nutrition_card

"""
Streamlit Thai Food Nutrition Analyzer
Refactored to organize related functions under `functions/` and templates under `templates/`.
"""

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="Thai Food Nutrition Analyzer",
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


def create_sample_data():
    sample = {
        'name': ['ต้มยำกุ้ง', 'ผัดไทย', 'แกงเผ็ดไก่', 'ส้มตำ', 'ข้าวผัด'],
        'ingredient': [
            '- กุ้งสด 200 กรัม\n- เห็ดฟาง 100 กรัม\n- มะนาว 2 ลูก\n- พริกขี้หนู 3 เม็ด\n- ตะไคร้ 2 ต้น',
            '- เส้นหมี่แห้ง 200 กรัม\n- ไข่ไก่ 2 ฟอง\n- ถั่วงอก 100 กรัม\n- กุ้งแห้ง 2 ช้อนโต๊ะ\n- น้ำตาลปี๊บ 2 ช้อนโต๊ะ',
            '- เนื้อไก่ 300 กรัม\n- มะเขือเปราะ 3 ลูก\n- พริกแกงเผ็ด 3 ช้อนโต๊ะ\n- กะทิ 400 มล.\n- ใบโหระพา',
            '- มะละกอดิบ 300 กรัม\n- มะเขือเทศ 2 ลูก\n- ถั่วฝักยาว 50 กรัม\n- กุ้งแห้ง 1 ช้อนโต๊ะ\n- พริกขี้หนู 5 เม็ด',
            '- ข้าวสวย 2 ถ้วย\n- ไข่ไก่ 2 ฟอง\n- หมูหั่นเต็ม 100 กรัม\n- ข้าวโพดอ่อน 50 กรัม\n- หอมใหญ่ 1 หัว'
        ],
        'method': [
            'ต้มน้ำให้เดือด ใส่ตะไคร้ ใส่กุ้งและเห็ด ปรุงรสด้วยมะนาวและพริก',
            'แช่เส้นหมี่ให้นิ่ม ผัดไข่ให้สุก ใส่เส้นหมี่ลงผัด ปรุงรสและใส่ถั่วงอก', 
            'ผัดพริกแกงกับกะทิให้หอม ใส่เนื้อไก่ ใส่มะเขือ ปรุงรสและใส่ใบโหระพา',
            'โขลกพริกขี้หนูกับกุ้งแห้ง ใส่มะละกอตำให้พอแหลก ใส่มะเขือเทศและถั่วฝักยาว ปรุงรส',
            'ตั้งกะทะใส่น้ำมัน ผัดไข่ให้สุก ใส่หมูผัดจนสุก ใส่ข้าวและข้าวโพด ปรุงรสตามชอบ'
        ]
    }
    return pd.DataFrame(sample)


# ฟังก์ชันหลัก
def main():
    # โหลดข้อมูลและโมเดลก่อน
    with st.spinner("กำลังโหลดระบบ..."):
        model = load_model()
        data = load_food_data()
        
        if data.empty:
            st.error("ไม่สามารถโหลดข้อมูลอาหารได้")
            return
        
        embeddings = get_embeddings(model, data)
        ingredient_embeddings = get_ingredient_embeddings(model, data)
        nutrition_calculator = SimpleNutritionCalculator()
    
    # ส่วนหัว (หลังจากโหลดโมเดลแล้ว)
    mode_indicator = "🤖 AI Enhanced" if SENTENCE_TRANSFORMERS_AVAILABLE and model else "🔍 Basic Mode"
    
    st.markdown(f"""
    <div class="main-header">
        <h1>🍲 ระบบวิเคราะห์คุณค่าทางโภชนาการอาหารไทย</h1>
        <p>Thai Food Nutrition Analyzer - {mode_indicator}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # แถบด้านข้าง
    with st.sidebar:
        st.markdown("## ⚙️ การตั้งค่า")
        
        # แสดงสถานะระบบ
        st.markdown("### 🖥️ สถานะระบบ")
        if SENTENCE_TRANSFORMERS_AVAILABLE and model:
            st.success("🤖 AI Search: พร้อมใช้งาน")
        else:
            st.warning("🔍 Basic Search: โหมดพื้นฐาน")
        
        if SKLEARN_AVAILABLE:
            st.success("📊 ML Tools: พร้อมใช้งาน")
        else:
            st.info("📊 ML Tools: ใช้ระบบทดแทน")
        
        # ตัวเลือกการค้นหา
        st.markdown("### 🔍 การค้นหา")
        search_mode = st.selectbox(
            "โหมดการค้นหา",
            ["อัตโนมัติ", "Fuzzy Search เท่านั้น"] if not SENTENCE_TRANSFORMERS_AVAILABLE 
            else ["อัตโนมัติ", "AI Search เท่านั้น", "Fuzzy Search เท่านั้น"],
            help="อัตโนมัติ = ใช้วิธีการที่ดีที่สุดที่มี"
        )
        
        max_results = st.slider(
            "จำนวนผลลัพธ์สูงสุด",
            1,
            int(max(1, len(data))),
            int(max(1, len(data)))
        )
        
        # ข้อมูลสถิติ
        st.markdown("### 📊 สถิติข้อมูล")
        st.metric("จำนวนสูตรอาหาร", len(data))
        
        # คำแนะนำสำหรับ AI features
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            st.markdown("### 💡 เพิ่ม AI Features")
            st.info("""
            เพื่อใช้งานฟีเจอร์ AI เต็มรูปแบบ:
            ```
            pip install sentence-transformers
            pip install scikit-learn
            ```
            """)
        
        # ข้อมูลเพิ่มเติม
        with st.expander("🔧 ข้อมูลเทคนิค", icon="▪️"):
            st.write(f"**Sentence Transformers:** {'✅' if SENTENCE_TRANSFORMERS_AVAILABLE else '❌'}")
            st.write(f"**Scikit-learn:** {'✅' if SKLEARN_AVAILABLE else '❌'}")
            st.write(f"**โหมดการทำงาน:** {'AI + Fuzzy' if model else 'Fuzzy Only'}")
            st.write(f"**ขนาด Embeddings:** {len(embeddings) if len(embeddings) > 0 else 'N/A'}")
    
    # แท็บหลัก
    tab1, tab2, tab3 = st.tabs(["🔍 ค้นหาอาหาร", "📋 ข้อมูลทั้งหมด", "ℹ️ เกี่ยวกับระบบ"])
    
    with tab1:
        st.markdown("## ค้นหาสูตรอาหารและวิเคราะห์คุณค่าทางโภชนาการ")
        
        # แสดงเคล็ดลับการค้นหา
        st.markdown("""
        <div class="search-tips">
            <h4>💡 เคล็ดลับการค้นหา:</h4>
            <ul>
                <li><strong>ชื่ออาหาร:</strong> ต้มยำกุ้ง, ผัดไทย, แกงเผ็ด</li>
                <li><strong>วัตถุดิบ:</strong> อาหารที่มีกุ้ง, เมนูไก่</li>
                <li><strong>รองรับการพิมพ์ผิด:</strong> ผัดใท → ผัดไทย</li>
                <li><strong>ภาษาอังกฤษ:</strong> tom yum, pad thai</li>
            </ul>
            """ + (f"""
            <div style="background: #e3f2fd; padding: 0.5rem; margin-top: 0.5rem; border-radius: 5px;">
                <strong>ℹ️ โหมดปัจจุบัน:</strong> {'AI + Fuzzy Search' if model and SENTENCE_TRANSFORMERS_AVAILABLE else 'Fuzzy Search (Basic)'}
            </div>
            """ if not SENTENCE_TRANSFORMERS_AVAILABLE else "") + """
        </div>
        """, unsafe_allow_html=True)
        
        # ช่องค้นหา
        query = st.text_input(
            "🔍 ค้นหาอาหารที่ต้องการ:",
            placeholder="เช่น ต้มยำกุ้ง, ผัดไทย, อาหารที่มีโปรตีนสูง...",
            help="พิมพ์ชื่ออาหาร วัตถุดิบ หรือคำอธิบายที่เกี่ยวข้อง"
        )
        
        if query:
            with st.spinner(f"กำลังค้นหา '{query}'..."):
                results = search_recipes(query, model, data, embeddings, ingredient_embeddings, max_results)
            
            if results:
                filtered_results = [r for r in results if r.get('similarity', 0) >= 0.5]
                st.markdown(f"### 🍽️ พบ {len(filtered_results)} รายการที่เกี่ยวข้อง (ความคล้ายคลึงมากกว่า 50%)")
                
                for i, result in enumerate(filtered_results, 1):
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
                            <div class=\"recipe-card\" style=\"background: #f8f9fa; border-left: 4px solid #17a2b8;\">
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
                - ลองค้นหาด้วยภาษาอังกฤษ
                """)
    
    with tab2:
        st.markdown("## 📋 ข้อมูลสูตรอาหารทั้งหมด")
        
        # ตัวกรองข้อมูล
        col1, col2, col3 = st.columns(3)
        
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
            
            # สถิติสรุป
            if len(nutrition_summary) > 0:
                st.markdown("### 📊 สถิติสรุป")
                col1, col2, col3, col4 = st.columns(4)
                
                avg_calories = np.mean([n.get('calories', 0) for n in nutrition_summary])
                avg_protein = np.mean([n.get('protein', 0) for n in nutrition_summary])
                avg_fat = np.mean([n.get('fat', 0) for n in nutrition_summary])
                avg_carbs = np.mean([n.get('carbs', 0) for n in nutrition_summary])
                
                with col1:
                    st.metric("แคลอรี่เฉลี่ย", f"{avg_calories:.0f} kcal")
                with col2:
                    st.metric("โปรตีนเฉลี่ย", f"{avg_protein:.1f} g")
                with col3:
                    st.metric("ไขมันเฉลี่ย", f"{avg_fat:.1f} g")
                with col4:
                    st.metric("คาร์โบไฮเดรตเฉลี่ย", f"{avg_carbs:.1f} g")
        else:
            st.info("ไม่พบข้อมูลที่ตรงกับเกณฑ์การกรอง")
    
    with tab3:
        st.markdown("## ℹ️ เกี่ยวกับระบบ")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            ### 🔬 เทคโนโลยีที่ใช้
            
            - **AI Search**: {'✅ Sentence Transformers' if SENTENCE_TRANSFORMERS_AVAILABLE else '❌ ไม่พร้อมใช้งาน'}
            - **โมเดล**: {'paraphrase-multilingual-MiniLM-L12-v2' if model else 'ไม่ได้โหลด'}
            - **การค้นหา**: {'Semantic + Fuzzy Matching' if SENTENCE_TRANSFORMERS_AVAILABLE else 'Fuzzy Matching Only'}
            - **ML Tools**: {'✅ Scikit-learn' if SKLEARN_AVAILABLE else '❌ ใช้ระบบทดแทน'}
            - **UI Framework**: ✅ Streamlit
            - **ข้อมูล**: สูตรอาหารไทยรวบรวม
            
            ### 🎯 คุณสมบัติปัจจุบัน
            
            - {'🤖' if SENTENCE_TRANSFORMERS_AVAILABLE else '🔍'} ค้นหาอาหาร{'ด้วย AI ที่เข้าใจภาษาไทย' if SENTENCE_TRANSFORMERS_AVAILABLE else 'แบบ Fuzzy Matching'}
            - ✅ รองรับการพิมพ์ผิด
            - ✅ คำนวณคุณค่าทางโภชนาการโดยประมาณ
            - ✅ แสดงผลแบบโต้ตอบที่สวยงาม
            - ✅ รองรับทั้งภาษาไทยและอังกฤษ
            """)
            
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                st.warning("""
                **💡 เพิ่มฟีเจอร์ AI:**
                
                เพื่อใช้งาน AI Search ให้ติดตั้ง:
                ```bash
                pip install sentence-transformers
                pip install scikit-learn torch
                ```
                """)
        
        with col2:
            st.markdown(f"""
            ### 📊 ข้อมูลในระบบ
            
            - **จำนวนสูตรอาหาร**: {len(data)} รายการ
            - **ประเภทข้อมูล**: สูตรอาหารไทยแท้
            - **การคำนวณโภชนาการ**: ระบบประมาณการอัตโนมัติ
            - **โหมดการทำงาน**: {'AI + Basic' if SENTENCE_TRANSFORMERS_AVAILABLE else 'Basic Only'}
            
            ### ⚠️ ข้อจำกัด
            
            - ค่าโภชนาการเป็นการประมาณจากข้อมูลพื้นฐาน
            - ความแม่นยำขึ้นอยู่กับคุณภาพข้อมูลต้นทาง
            - {'การค้นหา AI อาจไม่แม่นยำหากไม่มี Sentence Transformers' if not SENTENCE_TRANSFORMERS_AVAILABLE else 'การค้นหา AI ทำงานได้เต็มประสิทธิภาพ'}
            - ควรปรึกษาผู้เชี่ยวชาญด้านโภชนาการสำหรับการใช้งานทางการแพทย์
            
            ### 🔄 เวอร์ชัน
            
            - **เวอร์ชันปัจจุบัน**: {'2.0 Enhanced (Basic Mode)' if not SENTENCE_TRANSFORMERS_AVAILABLE else '2.0 Enhanced (Full AI)'}
            - **อัปเดตล่าสุด**: {datetime.now().strftime("%d/%m/%Y")}
            """)
        
        # ข้อมูลเพิ่มเติม
        st.markdown("### 🚀 การพัฒนาต่อ")
        
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            st.info("""
            **📱 โหมดปัจจุบัน: Basic Mode**
            
            แอปทำงานในโหมดพื้นฐานด้วย Fuzzy Search ที่ยังคงมีประสิทธิภาพดี
            
            **ฟีเจอร์ที่ทำงาน:**
            - ✅ การค้นหาแบบ Fuzzy Matching
            - ✅ รองรับการพิมพ์ผิด
            - ✅ การคำนวณโภชนาการ
            - ✅ UI ที่สวยงาม
            
            **เพื่อเปิดใช้ AI Features:**
            - ติดตั้ง sentence-transformers
            - ติดตั้ง scikit-learn
            - รีสตาร์ทแอป
            """)
        else:
            st.success("""
            **🤖 โหมดปัจจุบัน: AI Enhanced**
            
            แอปทำงานเต็มประสิทธิภาพด้วย AI Search
            
            **ฟีเจอร์ที่พร้อมใช้งาน:**
            - ✅ Semantic Search ด้วย AI
            - ✅ Fuzzy Search สำรอง
            - ✅ การจับคู่วัตถุดิบอัจฉริยะ
            - ✅ การคำนวณโภชนาการแบบครบถ้วน
            """)

if __name__ == "__main__":
    main()
