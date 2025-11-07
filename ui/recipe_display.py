"""
ui/recipe_display.py
UI Components สำหรับแสดงผลสูตรอาหาร
"""

import streamlit as st
from nutrition.calculator import calculate_nutrition
from ui.nutrition_display import display_nutrition


def get_similarity_badge(similarity_pct):
    """สร้าง badge ตามค่าความคล้าย"""
    if similarity_pct >= 90:
        return "🟢 ตรงมาก"
    elif similarity_pct >= 70:
        return "🟡 ค่อนข้างตรง"
    elif similarity_pct >= 50:
        return "🟠 ตรงปานกลาง"
    else:
        return "🔵 ตรงบางส่วน"


def render_recipe_card(result, index, nutrition_df):
    """
    แสดงการ์ดสูตรอาหาร
    
    Args:
        result: ข้อมูลสูตร
        index: ลำดับที่
        nutrition_df: DataFrame ข้อมูลโภชนาการ
    """
    similarity_pct = result['similarity'] * 100
    badge = get_similarity_badge(similarity_pct)
    
    with st.expander(
        f"{index}. 📖 {result['name']} | {badge} ({similarity_pct:.0f}%)",
        expanded=(index == 1)
    ):
        # ส่วนผสม
        st.markdown("### 🥘 ส่วนผสม")
        if result.get('ingredients'):
            st.text_area(
                "รายการส่วนผสม",
                result['ingredients'],
                height=150,
                disabled=True,
                label_visibility="collapsed",
                key=f"ingredients_{index}"
            )
        else:
            st.info("ไม่มีข้อมูลส่วนผสม")
        
        st.divider()
        
        # วิธีทำ
        st.markdown("### 👨‍🍳 วิธีทำ")
        if result.get('method'):
            st.text_area(
                "ขั้นตอนการทำ",
                result['method'],
                height=200,
                disabled=True,
                label_visibility="collapsed",
                key=f"method_{index}"
            )
        else:
            st.info("ไม่มีข้อมูลวิธีทำ")
        
        st.divider()
        
        # โภชนาการ
        st.markdown("### 📊 ข้อมูลโภชนาการ")
        
        if 'nutrition' in result:
            display_nutrition(result['nutrition'], result['name'])
        else:
            nutrition = calculate_nutrition(
                result.get('ingredients', ''),
                nutrition_df
            )
            
            if nutrition and 'total' in nutrition:
                display_nutrition(nutrition, result['name'])
            else:
                st.warning("⚠️ ไม่พบข้อมูลโภชนาการ")
                st.info("💡 ชื่อส่วนผสมในสูตรนี้อาจไม่ตรงกับฐานข้อมูล")


def render_recommended_recipes(recipes_df):
    """แสดงสูตรแนะนำ"""
    st.subheader("⭐ สูตรแนะนำ")
    st.markdown("*ลองค้นหาสูตรอาหารที่คุณสนใจ หรือเลือกดูจากสูตรแนะนำด้านล่าง*")
    
    recommended = recipes_df.sample(min(9, len(recipes_df)))
    
    # แสดงแบบ grid 3 คอลัมน์
    cols = st.columns(3)
    for idx, (_, recipe) in enumerate(recommended.iterrows()):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"**📖 {recipe['name']}**")
                
                # แสดงส่วนผสมย่อ
                ingredients_preview = str(recipe.get('ingredients', ''))[:100]
                if len(ingredients_preview) == 100:
                    ingredients_preview += "..."
                st.caption(f"🥘 {ingredients_preview}")
                
                # ปุ่มดูเพิ่มเติม
                if st.button(f"ดูรายละเอียด", key=f"rec_{idx}", use_container_width=True):
                    st.session_state['search_input'] = recipe['name']
                    st.rerun()


def render_search_results(results, nutrition_df):
    """แสดงผลการค้นหา"""
    if results:
        st.success(f"✅ พบ {len(results)} สูตรอาหาร")
        
        for i, result in enumerate(results, 1):
            render_recipe_card(result, i, nutrition_df)
    else:
        st.warning("😔 ไม่พบสูตรอาหารที่ตรงกับคำค้นหาและเกณฑ์ที่เลือก")
        st.info("💡 ลองค้นหาด้วยคำอื่น หรือลดค่า 'ความคล้ายขั้นต่ำ' หรือปรับเกณฑ์การกรอง")