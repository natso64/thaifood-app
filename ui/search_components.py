"""
ui/search_components.py
UI Components สำหรับส่วนค้นหา
"""

import streamlit as st


def render_search_input():
    """แสดง UI สำหรับค้นหา"""
    st.header("🔎 ค้นหาสูตรอาหาร")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input(
            "🔍 ค้นหาสูตร",
            placeholder="พิมพ์ชื่ออาหารหรือส่วนผสม เช่น ไก่, หมู, ผักกาด...",
            label_visibility="collapsed",
            key="search_input"
        )
    with col2:
        search_button = st.button("🔍 ค้นหา", use_container_width=True, type="primary")
    
    return search_query, search_button


def render_search_settings():
    """แสดง UI สำหรับตั้งค่าการค้นหา"""
    with st.expander("⚙️ การตั้งค่าการค้นหา", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            top_k = st.slider("📊 จำนวนผลลัพธ์", 1, 20, 10)
        
        with col2:
            min_similarity = st.slider("🎯 ความคล้ายขั้นต่ำ (%)", 0, 100, 30) / 100
    
    return top_k, min_similarity


def render_stats_metrics(num_recipes, num_ingredients):
    """แสดงสถิติพื้นฐาน"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📚 จำนวนสูตรอาหาร", num_recipes)
    
    with col2:
        st.metric("🥗 จำนวนส่วนผสม", num_ingredients)
    
    with col3:
        st.metric("📊 สถานะระบบ", "✅ พร้อมใช้งาน")