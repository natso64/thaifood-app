def get_total_grams(ingredient_name, amount_str, unit):
    """
    คำนวณน้ำหนักเป็นกรัม โดยเช็คตามลำดับความสำคัญ:
    1. Specific Density (แป้ง/น้ำมัน)
    2. Piece (ชิ้น/ลูก)
    3. Volume Standard (ช้อน/ถ้วย)
    """
    # 1. แปลงปริมาณเป็นตัวเลข (float)
    amount = parse_thai_quantity(amount_str)
    if amount == 0: return 0

    # 2. Check Specific Map (สำหรับของแห้ง/แป้ง/น้ำมัน ที่หน่วยตวงเพี้ยนง่าย)
    for key, unit_map in SPECIFIC_DENSITY_MAP.items():
        if key in ingredient_name:
            if unit in unit_map:
                return amount * unit_map[unit]

    # 3. Check Piece Map (สำหรับของเป็นชิ้น)
    for key, unit_map in PIECE_WEIGHT_MAP.items():
        if key in ingredient_name:
            if unit in unit_map:
                return amount * unit_map[unit]

    # 4. Check Volume Standard (สำหรับน้ำและของเหลวทั่วไป)
    if unit in VOLUME_WEIGHT_MAP:
        return amount * VOLUME_WEIGHT_MAP[unit]

    # กรณีไม่เจอหน่วยที่รู้จัก
    return None

# --- ตัวอย่างการทดสอบ ---
print(get_total_grams("แป้งข้าวจ้าว", "1+1/2", "ถ้วย"))
# ผลลัพธ์: 165.0 กรัม (1.5 * 110g จาก Specific Map)

print(get_total_grams("กุ้งนาง", "4", "ตัว"))
# ผลลัพธ์: 500.0 กรัม (4 * 125g จาก Piece Map)

print(get_total_grams("น้ำเปล่า", "1/2", "ถ้วย"))
# ผลลัพธ์: 120.0 กรัม (0.5 * 240g จาก Volume Map)