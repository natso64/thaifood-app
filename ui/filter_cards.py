"""
ui/filter_cards.py
UI Components สำหรับการ์ดกรองโภชนาการ
"""

import streamlit as st


# =====================================================
# CSS Styles
# =====================================================

def add_filter_cards_css():
    """เพิ่ม CSS สำหรับการ์ดกรองโภชนาการที่สวยงาม"""
    st.markdown("""
    <style>
    /* การ์ดแต่ละประเภทโภชนาการ */
    .nutrition-card-calories {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        margin-bottom: 1.2rem;
        color: white;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .nutrition-card-calories:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }
    
    .nutrition-card-protein {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        margin-bottom: 1.2rem;
        color: white;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .nutrition-card-protein:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }
    
    .nutrition-card-carbs {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        margin-bottom: 1.2rem;
        color: white;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .nutrition-card-carbs:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }
    
    .nutrition-card-fat {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        margin-bottom: 1.2rem;
        color: white;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .nutrition-card-fat:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }
    
    .nutrition-card-fiber {
        background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        margin-bottom: 1.2rem;
        color: white;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .nutrition-card-fiber:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }
    
    .nutrition-card-sodium {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        margin-bottom: 1.2rem;
        color: #333;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .nutrition-card-sodium:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }
    
    .nutrition-card-sugar {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        margin-bottom: 1.2rem;
        color: #333;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .nutrition-card-sugar:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }
    
    .nutrition-card-minerals {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        margin-bottom: 1.2rem;
        color: #333;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .nutrition-card-minerals:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }
    
    /* ส่วนหัวของการ์ด */
    .card-title {
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .card-icon {
        font-size: 1.8rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    /* ปรับแต่ง checkbox */
    .stCheckbox {
        background: rgba(255, 255, 255, 0.15);
        padding: 0.6rem;
        border-radius: 10px;
        margin-bottom: 0.6rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .stCheckbox:hover {
        background: rgba(255, 255, 255, 0.25);
        transform: translateX(8px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Mode selector card */
    .mode-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.8rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        margin: 1.5rem 0;
        color: white;
    }
    
    /* Selected filters summary card */
    .summary-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        margin: 1.2rem 0;
        color: white;
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .summary-item {
        background: rgba(255, 255, 255, 0.25);
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        margin: 0.4rem;
        display: inline-block;
        font-size: 0.95rem;
        font-weight: 500;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .summary-item:hover {
        background: rgba(255, 255, 255, 0.35);
        transform: scale(1.05);
    }
    
    /* ปุ่มล้างตัวกรอง */
    .clear-button {
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)


# =====================================================
# Filter Card Renderer
# =====================================================

def render_nutrition_card(title, icon, card_class, filters_data):
    """
    แสดงการ์ดโภชนาการแบบย่อ (ต่ำ / กลาง / สูง)

    ตอนนี้แต่ละการ์ดจะให้ผู้ใช้เลือกได้หนึ่งตัวเลือกจาก: ไม่เลือก, ต่ำ, กลาง, สูง
    ถ้าเลือก (ต่ำ/กลาง/สูง) จะคืนค่า filter tuple เดียวในรูปแบบ [(nutrient, op, value)]

    Args:
        title (str): ชื่อหมวดโภชนาการ
        icon (str): emoji icon
        card_class (str): CSS class ของการ์ด
        filters_data (list): รายการ tuple (label, filter_tuple) ที่มี 3 รายการ: ต่ำ, กลาง, สูง

    Returns:
        list: รายการ filter tuples ที่ถูกเลือก (0 หรือ 1 รายการ)
    """
    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="card-title"><span class="card-icon">{icon}</span> {title}</div>',
        unsafe_allow_html=True
    )

    # สร้างตัวเลือกแบบสั้น: ไม่เลือก / ต่ำ / กลาง / สูง
    labels = [label for label, _ in filters_data]
    options = ["ไม่เลือก"] + labels

    # unique key per card so Streamlit state is stable
    key = f"{title.replace(' ','_')}_level_select_v1"

    choice = st.radio("", options=options, index=0, horizontal=True, key=key, label_visibility="collapsed")

    selected_filters = []
    if choice != "ไม่เลือก":
        # หา filter tuple ที่แม็ปกับ label ที่เลือก
        for label, filter_tuple in filters_data:
            if label == choice:
                selected_filters.append(filter_tuple)
                break

    st.markdown('</div>', unsafe_allow_html=True)
    return selected_filters


# =====================================================
# Filter Data Definitions
# =====================================================

def get_calories_filters():
    """ข้อมูล filters สำหรับแคลอรี่"""
    return [
        ("ต่ำ", ('calories', '<', 100)),
        ("กลาง", ('calories', 'between', (100, 200))),
        ("สูง", ('calories', '>', 200)),
    ]


def get_protein_filters():
    """ข้อมูล filters สำหรับโปรตีน"""
    return [
        ("ต่ำ", ('protein', '<', 5)),
        ("กลาง", ('protein', 'between', (5, 15))),
        ("สูง", ('protein', '>', 15)),
    ]


def get_carbs_filters():
    """ข้อมูล filters สำหรับคาร์โบไฮเดรต"""
    return [
        ("ต่ำ", ('carbs', '<', 10)),
        ("กลาง", ('carbs', 'between', (10, 30))),
        ("สูง", ('carbs', '>', 30)),
    ]


def get_fat_filters():
    """ข้อมูล filters สำหรับไขมัน"""
    return [
        ("ต่ำ", ('fat', '<', 5)),
        ("กลาง", ('fat', 'between', (5, 15))),
        ("สูง", ('fat', '>', 15)),
    ]


def get_fiber_filters():
    """ข้อมูล filters สำหรับใยอาหาร"""
    return [
        ("ต่ำ", ('fiber', '<', 2)),
        ("กลาง", ('fiber', 'between', (2, 5))),
        ("สูง", ('fiber', '>', 5)),
    ]


def get_sodium_filters():
    """ข้อมูล filters สำหรับโซเดียม"""
    return [
        ("ต่ำ", ('sodium', '<', 200)),
        ("กลาง", ('sodium', 'between', (200, 500))),
        ("สูง", ('sodium', '>', 500)),
    ]


def get_sugar_filters():
    """ข้อมูล filters สำหรับน้ำตาล"""
    return [
        ("ต่ำ", ('sugar', '<', 5)),
        ("กลาง", ('sugar', 'between', (5, 10))),
        ("สูง", ('sugar', '>', 10)),
    ]


def get_calcium_filters():
    return [
        ("ต่ำ", ('calcium', '<', 50)),
        ("กลาง", ('calcium', 'between', (50, 100))),
        ("สูง", ('calcium', '>', 100)),
    ]


def get_iron_filters():
    return [
        ("ต่ำ", ('iron', '<', 1)),
        ("กลาง", ('iron', 'between', (1, 2))),
        ("สูง", ('iron', '>', 2)),
    ]


def get_potassium_filters():
    return [
        ("ต่ำ", ('potassium', '<', 150)),
        ("กลาง", ('potassium', 'between', (150, 300))),
        ("สูง", ('potassium', '>', 300)),
    ]


def get_vitamin_c_filters():
    return [
        ("ต่ำ", ('vitamin_c', '<', 5)),
        ("กลาง", ('vitamin_c', 'between', (5, 10))),
        ("สูง", ('vitamin_c', '>', 10)),
    ]


# =====================================================
# Main Filter Creator
# =====================================================

def create_nutrition_filters():
    """
    สร้าง UI สำหรับเลือก filters โภชนาการทั้งหมด
    
    Returns:
        list: รายการ filter tuples ที่ถูกเลือกทั้งหมด
    
    Example:
        >>> selected_filters = create_nutrition_filters()
        >>> print(selected_filters)
        [('calories', '<', 100), ('protein', '>', 15), ...]
    """
    all_selected_filters = []
    
    # 1. แคลอรี่
    all_selected_filters.extend(
        render_nutrition_card(
            "แคลอรี่", 
            "🔥", 
            "nutrition-card-calories", 
            get_calories_filters()
        )
    )
    
    # 2. โปรตีน
    all_selected_filters.extend(
        render_nutrition_card(
            "โปรตีน", 
            "💪", 
            "nutrition-card-protein", 
            get_protein_filters()
        )
    )
    
    # 3. คาร์โบไฮเดรต
    all_selected_filters.extend(
        render_nutrition_card(
            "คาร์โบไฮเดรต", 
            "🍚", 
            "nutrition-card-carbs", 
            get_carbs_filters()
        )
    )
    
    # 4. ไขมัน
    all_selected_filters.extend(
        render_nutrition_card(
            "ไขมัน", 
            "🧈", 
            "nutrition-card-fat", 
            get_fat_filters()
        )
    )
    
    # 5. ใยอาหาร
    all_selected_filters.extend(
        render_nutrition_card(
            "ใยอาหาร", 
            "🌾", 
            "nutrition-card-fiber", 
            get_fiber_filters()
        )
    )
    
    # 6. โซเดียม
    all_selected_filters.extend(
        render_nutrition_card(
            "โซเดียม", 
            "🧂", 
            "nutrition-card-sodium", 
            get_sodium_filters()
        )
    )
    
    # 7. น้ำตาล
    all_selected_filters.extend(
        render_nutrition_card(
            "น้ำตาล", 
            "🍬", 
            "nutrition-card-sugar", 
            get_sugar_filters()
        )
    )
    
    # 8. แร่ธาตุและวิตามิน (แยกเป็นการ์ดย่อยสำหรับแต่ละแร่/วิตามิน)
    all_selected_filters.extend(
        render_nutrition_card("แคลเซียม", "🧲", "nutrition-card-minerals", get_calcium_filters())
    )
    all_selected_filters.extend(
        render_nutrition_card("เหล็ก", "🧲", "nutrition-card-minerals", get_iron_filters())
    )
    all_selected_filters.extend(
        render_nutrition_card("โปแตสเซียม", "🧲", "nutrition-card-minerals", get_potassium_filters())
    )
    all_selected_filters.extend(
        render_nutrition_card("วิตามิน C", "🧲", "nutrition-card-minerals", get_vitamin_c_filters())
    )
    
    return all_selected_filters


# =====================================================
# Mode Selector
# =====================================================

def render_filter_mode_selector():
    """
    แสดง UI สำหรับเลือกโหมดการกรอง (any/all)
    
    Returns:
        str: โหมดการกรอง ("any" หรือ "all")
    """
    st.markdown('<div class="mode-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="card-title"><span class="card-icon">🎯</span> โหมดการกรอง</div>',
        unsafe_allow_html=True
    )
    
    match_mode = st.radio(
        "เลือกโหมดการกรอง",
        options=["any", "all"],
        format_func=lambda x: "✅ ตรงอย่างน้อย 1 เกณฑ์" if x == "any" else "✅ ตรงทุกเกณฑ์",
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # คำอธิบายเพิ่มเติม
    if match_mode == "any":
        st.caption("💡 แสดงสูตรที่ตรงเกณฑ์ที่เลือกไว้อย่างน้อย 1 ข้อ")
    else:
        st.caption("💡 แสดงเฉพาะสูตรที่ตรงเกณฑ์ที่เลือกไว้ทุกข้อ")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return match_mode


# =====================================================
# Filter Label Helper
# =====================================================

def get_filter_label(filter_tuple):
    """
    แปลง filter tuple เป็นข้อความแสดงผล
    
    Args:
        filter_tuple (tuple): (nutrient, operator, value)
    
    Returns:
        str: ข้อความแสดงผลพร้อม icon
    
    Example:
        >>> label = get_filter_label(('calories', '<', 100))
        >>> print(label)
        "🔥 แคลอรี่ < 100"
    """
    nutrient, operator, value = filter_tuple
    
    # Icon สำหรับแต่ละสารอาหาร
    nutrient_icons = {
        'calories': '🔥',
        'protein': '💪',
        'carbs': '🍚',
        'fat': '🧈',
        'fiber': '🌾',
        'sodium': '🧂',
        'sugar': '🍬',
        'calcium': '⚡',
        'iron': '⚡',
        'potassium': '⚡',
        'vitamin_c': '⚡'
    }
    
    # ชื่อสารอาหารภาษาไทย
    nutrient_names = {
        'calories': 'แคลอรี่',
        'protein': 'โปรตีน',
        'carbs': 'คาร์โบไฮเดรต',
        'fat': 'ไขมัน',
        'fiber': 'ใยอาหาร',
        'sodium': 'โซเดียม',
        'sugar': 'น้ำตาล',
        'calcium': 'แคลเซียม',
        'iron': 'เหล็ก',
        'potassium': 'โปแตสเซียม',
        'vitamin_c': 'วิตามิน C'
    }
    
    icon = nutrient_icons.get(nutrient, '📊')
    name = nutrient_names.get(nutrient, nutrient)
    
    # สร้างข้อความตาม operator
    if operator == '<':
        return f"{icon} {name} น้อยกว่า {value}"
    elif operator == '>':
        return f"{icon} {name} มากกว่า {value}"
    elif operator == 'between':
        return f"{icon} {name} ระหว่าง {value[0]}-{value[1]}"
    
    return str(filter_tuple)


# =====================================================
# Selected Filters Summary
# =====================================================

def render_selected_filters_summary(selected_filters):
    """
    แสดงสรุปเกณฑ์ที่เลือกในรูปแบบการ์ดสวยงาม
    
    Args:
        selected_filters (list): รายการ filter tuples ที่ถูกเลือก
    """
    if not selected_filters:
        return
    
    st.markdown('<div class="summary-card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="card-title">'
        f'<span class="card-icon">📋</span> '
        f'เกณฑ์ที่เลือก ({len(selected_filters)} เกณฑ์)'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # สร้าง HTML tags สำหรับแต่ละ filter
    filter_labels_html = ""
    for filter_tuple in selected_filters:
        label = get_filter_label(filter_tuple)
        filter_labels_html += f'<span class="summary-item">{label}</span> '
    
    st.markdown(filter_labels_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================
# Quick Filter Presets (เพิ่มเติม)
# =====================================================

def get_filter_presets():
    """
    ชุด filters สำเร็จรูปสำหรับความต้องการเฉพาะ
    
    Returns:
        dict: ชุด preset filters
    """
    return {
        "🏃 ลดน้ำหนัก": [
            ('calories', '<', 100),
            ('fat', '<', 5),
            ('fiber', '>', 5),
        ],
        "💪 เพิ่มกล้ามเนื้อ": [
            ('protein', '>', 25),
            ('calories', '>', 200),
        ],
        "🩺 เบาหวาน": [
            ('carbs', '<', 10),
            ('sugar', '<', 5),
            ('fiber', '>', 5),
        ],
        "🥑 Keto": [
            ('carbs', '<', 5),
            ('fat', '>', 15),
            ('protein', '>', 15),
        ],
        "❤️ ความดันสูง": [
            ('sodium', '<', 200),
            ('potassium', '>', 300),
            ('fat', '<', 5),
        ],
    }


def render_filter_presets():
    """แสดง UI สำหรับเลือก preset filters"""
    st.markdown("### 🎯 เทมเพลตสำเร็จรูป")
    st.caption("เลือกเทมเพลตตามความต้องการของคุณ")
    
    presets = get_filter_presets()
    
    cols = st.columns(len(presets))
    selected_preset = None
    
    for idx, (preset_name, preset_filters) in enumerate(presets.items()):
        with cols[idx]:
            if st.button(preset_name, use_container_width=True):
                selected_preset = preset_filters
    
    return selected_preset