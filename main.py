"""
main.py
ไฟล์หลักสำหรับรัน Streamlit Application
"""

import streamlit as st
import pandas as pd

from config import PAGE_TITLE, PAGE_ICON, RECIPES_CSV
from models.model_loader import load_model
from models.embeddings import get_name_embeddings, get_ingredient_embeddings
from nutrition.data_loader import load_nutrition_data
from search.semantic_search import search_recipes
from nutrition.calculator import calculate_nutrition

# Import UI Components
from ui.filter_cards import (
    add_filter_cards_css,
    create_nutrition_filters,
    render_filter_mode_selector,
    render_selected_filters_summary
)
from ui.search_components import (
    render_search_input,
    render_search_settings,
    render_stats_metrics
)
from ui.recipe_display import (
    render_search_results,
    render_recommended_recipes
)


def apply_nutrition_filters(results, selected_filters, match_mode, nutrition_df):
    """
    กรองผลลัพธ์ตามเกณฑ์โภชนาการ
    
    Args:
        results: ผลลัพธ์การค้นหา
        selected_filters: เกณฑ์ที่เลือก
        match_mode: โหมดการกรอง ('any' หรือ 'all')
        nutrition_df: DataFrame ข้อมูลโภชนาการ
    
    Returns:
        list: ผลลัพธ์ที่ผ่านการกรอง
    """
    if not selected_filters:
        return results
    
    filtered_results = []
    
    for result in results:
        nutrition = calculate_nutrition(
            result.get('ingredients', ''),
            nutrition_df
        )
        
        if nutrition and 'total' in nutrition:
            result['nutrition'] = nutrition
            
            # ตรวจสอบว่าตรงกับ filters หรือไม่
            match_count = 0
            for nutrient, operator, value in selected_filters:
                nutrient_value = nutrition['total'].get(nutrient, 0)
                
                if operator == '<':
                    if nutrient_value < value:
                        match_count += 1
                elif operator == '>':
                    if nutrient_value > value:
                        match_count += 1
                elif operator == 'between':
                    if value[0] <= nutrient_value <= value[1]:
                        match_count += 1
            
            # ตัดสินใจตาม match_mode
            if match_mode == 'any' and match_count > 0:
                filtered_results.append(result)
            elif match_mode == 'all' and match_count == len(selected_filters):
                filtered_results.append(result)
    
    return filtered_results


def main():
    # ตั้งค่าหน้าเว็บ
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # เพิ่ม CSS
    add_filter_cards_css()
    
    # หัวข้อ
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
    
    # แสดงสถิติ
    render_stats_metrics(len(recipes_df), len(nutrition_df))
    
    st.divider()
    
    # ===== โหลด Model & Embeddings =====
    model = load_model()
    name_embeddings = get_name_embeddings(model, recipes_df)
    ingredient_embeddings = get_ingredient_embeddings(model, recipes_df)
    
    # ===== UI ส่วนค้นหา =====
    search_query, search_button = render_search_input()
    top_k, min_similarity = render_search_settings()
    
    st.divider()
    
    # ===== UI Filters =====
    with st.expander("🎛️ กรองตามค่าโภชนาการ", expanded=False):
        selected_filters = create_nutrition_filters()
        match_mode = render_filter_mode_selector()
        
        # แสดงสรุปเกณฑ์ที่เลือก
        render_selected_filters_summary(selected_filters)
        
        # ปุ่มล้างตัวกรอง
        if selected_filters and st.button("🔄 ล้างตัวกรองทั้งหมด", use_container_width=True):
            st.rerun()
    
    st.divider()
    
    # ===== แสดงผลการค้นหา =====
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
            
            # กรองด้วย nutrition filters
            if results and selected_filters:
                with st.spinner("🔄 กำลังกรองตามโภชนาการ..."):
                    results = apply_nutrition_filters(
                        results, selected_filters, match_mode, nutrition_df
                    )
            
            # แสดงผลลัพธ์
            render_search_results(results, nutrition_df)
        else:
            st.error("❌ ไม่สามารถโหลด AI Model ได้")
    
    elif not search_query:
        # แสดงสูตรแนะนำ
        render_recommended_recipes(recipes_df)
    
    # ===== Footer =====
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🍲 ระบบค้นหาและวิเคราะห์โภชนาการอาหารไทย | Made with ❤️ using Streamlit</p>
        <p style='font-size: 0.8em;'>💡 <b>เคล็ดลับ:</b> ใช้ตัวกรองเพื่อค้นหาสูตรอาหารที่ตรงตามความต้องการของคุณ</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()