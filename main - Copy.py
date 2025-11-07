"""
main.py
ไฟล์หลักสำหรับรัน Streamlit Application
"""

import streamlit as st
import pandas as pd
import numpy as np

from config import PAGE_TITLE, PAGE_ICON, RECIPES_CSV
from models.model_loader import load_model
from models.embeddings import get_name_embeddings, get_ingredient_embeddings
from nutrition.data_loader import load_nutrition_data
from search.semantic_search import search_recipes
from search.nutrition_filter import filter_recipes_by_nutrition
from ui.filters_ui import create_nutrition_filter_ui
from ui.search_results import display_filtered_results
from ui.nutrition_display import display_nutrition
from nutrition.calculator import calculate_nutrition
from utils.constants import THAI_NAMES


def main():
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title(f"{PAGE_ICON} {PAGE_TITLE}")
    
    # ===== โหลดข้อมูล =====
    with st.spinner("กำลังโหลดข้อมูล..."):
        nutrition_df = load_nutrition_data()
        
        try:
            recipes_df = pd.read_csv(RECIPES_CSV)
        except FileNotFoundError:
            st.error(f"❌ ไม่พบไฟล์ {RECIPES_CSV}")
            st.info(f"📁 กรุณาวางไฟล์ recipes.csv ในโฟลเดอร์ data/")
            return
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")
            return
    
    if nutrition_df.empty or recipes_df.empty:
        st.error("❌ กรุณาตรวจสอบไฟล์ข้อมูล")
        return
    
    # แสดงข้อมูลสถิติพื้นฐาน
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 จำนวนสูตรอาหาร", len(recipes_df))
    with col2:
        st.metric("🥗 จำนวนส่วนผสม", len(nutrition_df))
    with col3:
        st.metric("📊 สถานะระบบ", "✅ พร้อมใช้งาน")
    
    st.divider()
    
    # ===== โหลด Model & Embeddings =====
    model = load_model()
    name_embeddings = get_name_embeddings(model, recipes_df)
    ingredient_embeddings = get_ingredient_embeddings(model, recipes_df)
    
    # ===== Sidebar Filters =====
    selected_filters, match_mode = create_nutrition_filter_ui()
    
    # ===== Main Tabs =====
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 กรองตามโภชนาการ",
        "🔎 ค้นหาสูตรอาหาร",
        "📊 สถิติโภชนาการ",
        "➕ คำนวณโภชนาการเอง"
    ])
    
    # ========== TAB 1: กรองตามโภชนาการ ==========
    with tab1:
        st.header("🔍 ค้นหาด้วยเกณฑ์โภชนาการ")
        
        if selected_filters:
            st.info(f"🎯 เลือกเกณฑ์แล้ว {len(selected_filters)} เกณฑ์")
            
            # แสดงเกณฑ์ที่เลือก
            with st.expander("📋 เกณฑ์ที่เลือก", expanded=True):
                from ui.search_results import get_matched_labels
                labels = get_matched_labels(selected_filters)
                for i, label in enumerate(labels, 1):
                    st.write(f"{i}. {label}")
            
            # ปุ่มค้นหา
            if st.button("🔍 ค้นหาสูตรอาหาร", type="primary", use_container_width=True):
                with st.spinner("🔄 กำลังคำนวณโภชนาการและกรอง..."):
                    results = filter_recipes_by_nutrition(
                        recipes_df,
                        nutrition_df,
                        selected_filters,
                        match_mode=match_mode,
                        top_k=20
                    )
                
                display_filtered_results(results, nutrition_df)
        else:
            st.info("👈 กรุณาเลือกเกณฑ์โภชนาการจาก Sidebar ด้านซ้าย")
            
            # คู่มือการใช้งาน
            with st.expander("📖 คู่มือการใช้งาน", expanded=True):
                st.markdown("""
                ### 🎯 วิธีใช้งาน:
                1. **เลือกเกณฑ์** จาก Sidebar ด้านซ้าย (คลิกที่กลุ่มโภชนาการ)
                2. **เลือกโหมด** การกรอง:
                   - **ตรงอย่างน้อย 1 เกณฑ์**: แสดงสูตรที่ตรงบางเกณฑ์
                   - **ตรงทุกเกณฑ์**: แสดงเฉพาะสูตรที่ตรงทุกเกณฑ์
                3. **กดค้นหา** เพื่อดูผลลัพธ์
                
                ### 💡 ตัวอย่างการใช้งาน:
                
                **🏃 ลดน้ำหนัก:**
                - เลือก: แคลอรี่ต่ำ + ไขมันต่ำ + ใยอาหารสูง
                
                **💪 เพิ่มกล้ามเนื้อ:**
                - เลือก: โปรตีนสูง + แคลอรี่สูง
                
                **🩺 เบาหวาน:**
                - เลือก: คาร์โบต่ำ + ใยอาหารสูง + โซเดียมต่ำ
                
                **🥑 Keto Diet:**
                - เลือก: คาร์โบต่ำมาก + ไขมันสูง + โปรตีนสูง
                
                **❤️ ความดันสูง:**
                - เลือก: โซเดียมต่ำ + โปแตสเซียมสูง + ไขมันต่ำ
                """)
    
    # ========== TAB 2: ค้นหาสูตรอาหาร ==========
    with tab2:
        st.header("🔎 ค้นหาสูตรอาหาร")
        
        # ช่องค้นหา
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input(
                "🔍 ค้นหาสูตร",
                placeholder="พิมพ์ชื่ออาหารหรือส่วนผสม เช่น ไก่, ผัดไทย, ต้มยำ...",
                label_visibility="collapsed"
            )
        with col2:
            search_button = st.button("🔍 ค้นหา", use_container_width=True)
        
        # การตั้งค่าขั้นสูง
        with st.expander("⚙️ การตั้งค่าขั้นสูง"):
            col1, col2 = st.columns(2)
            with col1:
                top_k = st.slider("จำนวนผลลัพธ์", 1, 20, 5)
            with col2:
                min_similarity = st.slider("ความคล้ายขั้นต่ำ (%)", 0, 100, 30) / 100
        
        # ค้นหา
        if (search_query and search_button) or (search_query and len(search_query) > 2):
            if model is not None:
                with st.spinner("🔄 กำลังค้นหา..."):
                    results = search_recipes(
                        query=search_query,
                        model=model,
                        data=recipes_df,
                        name_embeddings=name_embeddings,
                        ingredient_embeddings=ingredient_embeddings,
                        top_k=top_k,
                        min_similarity=min_similarity
                    )
                
                if results:
                    st.success(f"✅ พบ {len(results)} สูตรอาหาร")
                    
                    for i, result in enumerate(results, 1):
                        similarity_pct = result['similarity'] * 100
                        
                        # กำหนดสีตามความคล้าย
                        if similarity_pct >= 90:
                            badge = "🟢 ตรงมาก"
                        elif similarity_pct >= 70:
                            badge = "🟡 ค่อนข้างตรง"
                        elif similarity_pct >= 50:
                            badge = "🟠 ตรงปานกลาง"
                        else:
                            badge = "🔵 ตรงบางส่วน"
                        
                        with st.expander(
                            f"{i}. 📖 {result['name']} | {badge} ({similarity_pct:.0f}%)",
                            expanded=(i == 1)
                        ):
                            # Tabs ย่อย
                            subtab1, subtab2, subtab3 = st.tabs([
                                "📊 โภชนาการ",
                                "🥘 ส่วนผสม",
                                "👨‍🍳 วิธีทำ"
                            ])
                            
                            with subtab1:
                                nutrition = calculate_nutrition(
                                    result['ingredients'],
                                    nutrition_df
                                )
                                display_nutrition(nutrition, result['name'])
                            
                            with subtab2:
                                st.markdown("### 🥘 ส่วนผสม")
                                st.text(result['ingredients'] if result['ingredients'] else "ไม่มีข้อมูล")
                            
                            with subtab3:
                                st.markdown("### 👨‍🍳 วิธีทำ")
                                st.text(result['method'] if result['method'] else "ไม่มีข้อมูล")
                else:
                    st.warning("😔 ไม่พบสูตรอาหารที่ตรงกับคำค้นหา")
                    st.info("💡 ลองค้นหาด้วยคำอื่น หรือลดค่า 'ความคล้ายขั้นต่ำ'")
            else:
                st.error("❌ ไม่สามารถโหลด AI Model ได้")
        elif not search_query:
            # แสดงสูตรแนะนำ
            st.subheader("⭐ สูตรแนะนำ")
            recommended = recipes_df.sample(min(6, len(recipes_df)))
            
            cols = st.columns(3)
            for idx, (_, recipe) in enumerate(recommended.iterrows()):
                with cols[idx % 3]:
                    with st.container():
                        st.markdown(f"**{recipe['name']}**")
                        if st.button(f"ดูรายละเอียด", key=f"rec_{idx}"):
                            st.session_state['selected_recipe'] = recipe
    
    # ========== TAB 3: สถิติโภชนาการ ==========
    with tab3:
        st.header("📊 สถิติโภชนาการรวม")
        
        with st.spinner("🔄 กำลังคำนวณสถิติ..."):
            # คำนวณโภชนาการทั้งหมด
            all_nutrition = []
            for idx, recipe in recipes_df.iterrows():
                nutrition = calculate_nutrition(
                    recipe.get('ingredient', ''),
                    nutrition_df
                )
                if nutrition and 'total' in nutrition:
                    nutrition_record = nutrition['total'].copy()
                    nutrition_record['recipe_name'] = recipe['name']
                    all_nutrition.append(nutrition_record)
        
        if all_nutrition:
            stats_df = pd.DataFrame(all_nutrition)
            
            # ===== ค่าเฉลี่ยโภชนาการ =====
            st.subheader("📈 ค่าเฉลี่ยโภชนาการต่อสูตร")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_cal = stats_df['calories'].mean()
                st.metric(
                    "🔥 แคลอรี่เฉลี่ย",
                    f"{avg_cal:.0f} kcal",
                    delta=f"สูงสุด: {stats_df['calories'].max():.0f}"
                )
            
            with col2:
                avg_protein = stats_df['protein'].mean()
                st.metric(
                    "💪 โปรตีนเฉลี่ย",
                    f"{avg_protein:.1f} g",
                    delta=f"สูงสุด: {stats_df['protein'].max():.1f}"
                )
            
            with col3:
                avg_carbs = stats_df['carbs'].mean()
                st.metric(
                    "⚡ คาร์โบเฉลี่ย",
                    f"{avg_carbs:.1f} g",
                    delta=f"สูงสุด: {stats_df['carbs'].max():.1f}"
                )
            
            with col4:
                avg_fat = stats_df['fat'].mean()
                st.metric(
                    "🧈 ไขมันเฉลี่ย",
                    f"{avg_fat:.1f} g",
                    delta=f"สูงสุด: {stats_df['fat'].max():.1f}"
                )
            
            st.divider()
            
            # ===== ตารางสถิติเต็ม =====
            st.subheader("📋 ตารางสถิติโดยละเอียด")
            
            # เลือกสารอาหารที่จะแสดง
            nutrients_to_show = st.multiselect(
                "เลือกสารอาหารที่ต้องการดู",
                options=list(THAI_NAMES.keys()),
                default=['calories', 'protein', 'carbs', 'fat'],
                format_func=lambda x: THAI_NAMES[x]
            )
            
            if nutrients_to_show:
                stats_summary = stats_df[nutrients_to_show].describe()
                
                # แปลงชื่อ columns เป็นภาษาไทย
                stats_summary.columns = [THAI_NAMES[col] for col in stats_summary.columns]
                
                st.dataframe(
                    stats_summary.style.format("{:.2f}"),
                    use_container_width=True
                )
            
            st.divider()
            
            # ===== Top 5 =====
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏆 Top 5 สูตรแคลอรี่สูงสุด")
                top_calories = stats_df.nlargest(5, 'calories')[['recipe_name', 'calories']]
                for idx, row in top_calories.iterrows():
                    st.write(f"**{row['recipe_name']}**: {row['calories']:.0f} kcal")
            
            with col2:
                st.subheader("🥇 Top 5 สูตรโปรตีนสูงสุด")
                top_protein = stats_df.nlargest(5, 'protein')[['recipe_name', 'protein']]
                for idx, row in top_protein.iterrows():
                    st.write(f"**{row['recipe_name']}**: {row['protein']:.1f} g")
            
            st.divider()
            
            # ===== กราฟแสดงการกระจาย =====
            st.subheader("📊 การกระจายของค่าโภชนาการ")
            
            chart_nutrient = st.selectbox(
                "เลือกสารอาหารที่ต้องการดูกราฟ",
                options=['calories', 'protein', 'carbs', 'fat'],
                format_func=lambda x: THAI_NAMES[x]
            )
            
            # สร้างกราฟ histogram
            import plotly.express as px
            
            fig = px.histogram(
                stats_df,
                x=chart_nutrient,
                nbins=30,
                title=f"การกระจายของ{THAI_NAMES[chart_nutrient]}",
                labels={chart_nutrient: THAI_NAMES[chart_nutrient]}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.warning("⚠️ ไม่สามารถคำนวณสถิติได้")
    
    # ========== TAB 4: คำนวณโภชนาการเอง ==========
    with tab4:
        st.header("➕ คำนวณโภชนาการจากส่วนผสมของคุณ")
        
        st.markdown("""
        ### 📝 วิธีใช้งาน:
        ระบุส่วนผสมและปริมาณในรูปแบบ: **ชื่อส่วนผสม + ปริมาณ + หน่วย**
        
        **ตัวอย่าง:**
        ```
        ไก่ 200 กรัม
        น้ำมันมะกอก 2 ช้อนโต๊ะ
        กระเทียม 3 กลีบ
        ผักบุ้ง 100 กรัม
        น้ำปลา 1 ช้อนโต๊ะ
        ```
        """)
        
        # ช่องกรอกส่วนผสม
        ingredient_input = st.text_area(
            "📋 ระบุส่วนผสมและปริมาณ",
            height=200,
            placeholder="ไก่ 200 กรัม\nน้ำมัน 2 ช้อนโต๊ะ\nกระเทียม 3 กลีบ",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns([2, 1])
        with col1:
            recipe_name_input = st.text_input("📖 ชื่อสูตร (ถ้ามี)", placeholder="เช่น ผัดผักบุ้งไก่")
        
        # ปุ่มคำนวณ
        if st.button("🧮 คำนวณโภชนาการ", type="primary", use_container_width=True):
            if ingredient_input.strip():
                with st.spinner("🔄 กำลังคำนวณ..."):
                    nutrition = calculate_nutrition(ingredient_input, nutrition_df)
                    
                    if nutrition and 'total' in nutrition:
                        display_nutrition(
                            nutrition,
                            recipe_name_input if recipe_name_input else "สูตรของคุณ"
                        )
                    else:
                        st.warning("⚠️ ไม่พบข้อมูลโภชนาการของส่วนผสมบางตัว")
                        st.info("💡 ลองตรวจสอบชื่อส่วนผสมว่าถูกต้องหรือไม่")
            else:
                st.warning("⚠️ กรุณาระบุส่วนผสม")
        
        # แสดงตัวอย่างส่วนผสมที่มีในฐานข้อมูล
        with st.expander("📚 ดูรายชื่อส่วนผสมที่มีในฐานข้อมูล"):
            st.dataframe(
                nutrition_df[['ingredient']].head(20),
                use_container_width=True,
                hide_index=True
            )
            st.info(f"📊 รวมทั้งหมด {len(nutrition_df)} รายการ")


if __name__ == "__main__":
    main()