"""
ui/filters_ui.py
UI สำหรับ Nutrition Filters
"""

import streamlit as st
from typing import Tuple, List
from utils.constants import NUTRITION_FILTER_GROUPS


def create_nutrition_filter_ui() -> Tuple[List[str], str]:
    """สร้าง UI สำหรับเลือก nutrition filters"""
    
    st.sidebar.header("🔍 กรองตามโภชนาการ")
    
    match_mode = st.sidebar.radio(
        "โหมดการกรอง",
        options=['any', 'all'],
        format_func=lambda x: 'ตรงอย่างน้อย 1 เกณฑ์' if x == 'any' else 'ตรงทุกเกณฑ์',
        help="เลือกว่าต้องการให้ตรงทุกเกณฑ์หรือเพียงบางเกณฑ์"
    )
    
    selected_filters = []
    
    for group_name, filters in NUTRITION_FILTER_GROUPS.items():
        with st.sidebar.expander(f"📊 {group_name}", expanded=False):
            for display_name, filter_key in filters.items():
                if st.checkbox(display_name, key=filter_key):
                    selected_filters.append(filter_key)
    
    if selected_filters:
        st.sidebar.success(f"✅ เลือกแล้ว {len(selected_filters)} เกณฑ์")
    
    if st.sidebar.button("🗑️ ล้างทั้งหมด"):
        st.rerun()
    
    return selected_filters, match_mode