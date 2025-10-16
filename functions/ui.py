import re
import streamlit as st


def display_ingredients(ingredients_text: str):
    if not ingredients_text:
        return
    st.markdown("### 🥘 วัตถุดิบ")
    ingredients = [line.strip() for line in ingredients_text.split('\n') if line.strip()]
    formatted_ingredients = []
    for ingredient in ingredients:
        clean_ingredient = re.sub(r'^[-•*]\s*', '', ingredient)
        if clean_ingredient:
            formatted_ingredients.append(f"• {clean_ingredient}")
    ingredients_html = "<br>".join(formatted_ingredients)
    st.markdown(f"""
    <div class="ingredient-list">
        {ingredients_html}
    </div>
    """, unsafe_allow_html=True)


def display_nutrition_card(nutrition_data):
    st.markdown("### 📊 ค่าโภชนาการ")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="nutrition-metric">
            <h4>🔥 แคลอรี่</h4>
            <h2>{nutrition_data.get('calories', 0):.0f}</h2>
            <p>kcal</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="nutrition-metric">
            <h4>🥩 โปรตีน</h4>
            <h2>{nutrition_data.get('protein', 0):.1f}</h2>
            <p>g</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="nutrition-metric">
            <h4>🥑 ไขมัน</h4>
            <h2>{nutrition_data.get('fat', 0):.1f}</h2>
            <p>g</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="nutrition-metric">
            <h4>🍞 คาร์โบไฮเดรต</h4>
            <h2>{nutrition_data.get('carbs', 0):.1f}</h2>
            <p>g</p>
        </div>
        """, unsafe_allow_html=True)


