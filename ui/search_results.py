"""
ui/search_results.py
แสดงผลการค้นหา
"""

import streamlit as st
from typing import List, Dict
from ui.nutrition_display import display_nutrition
from utils.constants import NUTRITION_FILTER_GROUPS


def display_filtered_results(results: List[Dict], nutrition_df):
    """แสดงผลลัพธ์ที่กรองแล้ว"""
    
    if not results:
        st.warning("😔 ไม่พบสูตรอาหารที่ตรงตามเกณฑ์")
        return
    
    st.success(f"🎯 พบ {len(results)} สูตรอาหารที่ตรงตามเกณฑ์")
    
    # สถิติรวม
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_match = sum(r['match_percentage'] for r in results) / len(results)
        st.metric("ค่าเฉลี่ยความตรง", f"{avg_match:.0f}%")
    with col2:
        max_score = max(r['score'] for r in results)
        st.metric("คะแนนสูงสุด", f"{max_score}")
    with col3:
        st.metric("จำนวนสูตร", len(results))
    
    # แสดงแต่ละสูตร
    for i, result in enumerate(results, 1):
        recipe = result['recipe']
        nutrition = result['nutrition']
        
        with st.expander(
            f"{i}. ⭐ {recipe['name']} "
            f"(ตรง {result['match_percentage']:.0f}% | คะแนน {result['score']})",
            expanded=(i <= 3)
        ):
            # เกณฑ์ที่ตรง
            st.markdown("**✅ ตรงตามเกณฑ์:**")
            matched_labels = get_matched_labels(result['matched_filters'])
            st.write(", ".join(f"`{label}`" for label in matched_labels))
            
            # แท็บข้อมูล
            tab1, tab2, tab3 = st.tabs(["📊 โภชนาการ", "🥘 ส่วนผสม", "👨‍🍳 วิธีทำ"])
            
            with tab1:
                display_nutrition(nutrition, recipe['name'])
            with tab2:
                st.text(recipe.get('ingredient', 'ไม่มีข้อมูล'))
            with tab3:
                st.text(recipe.get('method', 'ไม่มีข้อมูล'))


def get_matched_labels(matched_filters: List[str]) -> List[str]:
    """แปลง filter keys เป็นชื่อที่แสดง"""
    matched_labels = []
    for filter_key in matched_filters:
        for group_filters in NUTRITION_FILTER_GROUPS.values():
            for display_name, key in group_filters.items():
                if key == filter_key:
                    matched_labels.append(display_name)
                    break
    return matched_labels