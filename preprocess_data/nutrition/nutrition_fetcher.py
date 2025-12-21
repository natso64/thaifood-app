import pandas as pd
import requests
import time

from preprocess_data.nutrition.nutrition_map import USDA_MAP

# ==========================================
# 1. ตั้งค่า API และ Mapping (ส่วนสำคัญ)
# ==========================================
API_KEY = 'NkONT9cAyvhKXmIwf4c3HK3QE8qT8F8ohq6fbdTu'  # <--- !!! ใส่ API Key ของคุณที่นี่ !!!
BASE_URL = 'https://api.nal.usda.gov/fdc/v1/foods/search'

# สกัดเอาเฉพาะชื่อภาษาอังกฤษที่ไม่ซ้ำกันมาดึงข้อมูล
unique_usda_names = list(set(USDA_MAP.values()))

# ID สารอาหาร
NUTRIENT_MAP = {
    1008: 'calories', 1003: 'protein', 1005: 'carbs', 1004: 'fat',
    1079: 'fiber', 1106: 'vitamin_a', 1162: 'vitamin_c',
    1165: 'vitamin_b1', 1166: 'vitamin_b2', 1087: 'calcium',
    1089: 'iron', 1092: 'potassium', 1093: 'sodium'
}

def fetch_per_100g(query_name):
    if not query_name or 'NOT_FOUND' in query_name: return None

    try:
        resp = requests.get(BASE_URL, params={
            'api_key': API_KEY, 'query': query_name, 'pageSize': 3,  # <--- เพิ่มจำนวน search result
            'dataType': ['Survey (FNDDS)', 'Foundation', 'SR Legacy'] # เรียงลำดับความสำคัญ
        })
        if resp.status_code == 200:
            data = resp.json()
            if data['foods']:
                food = data['foods'][0]
                nutrients = food.get('foodNutrients', [])

                # เก็บค่าต่อ 100g
                row = {'usda_name': query_name}
                for n in nutrients:
                    if n['nutrientId'] in NUTRIENT_MAP:
                        row[NUTRIENT_MAP[n['nutrientId']]] = n['value']
                return row
        elif resp.status_code == 429:
            time.sleep(10)
            return fetch_per_100g(query_name)
    except Exception as e:
        print(f"Error: {e}")
    return None

# 1. ดึงข้อมูลมาเก็บใส่ Dictionary กลางไว้ก่อน (เพื่อไม่ให้ดึงซ้ำ)
nutrition_cache = {}
print(f"กำลังดึงข้อมูลจาก {len(unique_usda_names)} รายการที่ไม่ซ้ำ...")

for i, name in enumerate(unique_usda_names):
    print(f"[{i+1}/{len(unique_usda_names)}] Fetching: {name}")
    data = fetch_per_100g(name)
    if data:
        # เติมค่า 0 ถ้าไม่มีข้อมูล
        for col in NUTRIENT_MAP.values():
            if col not in data: data[col] = 0.0
        nutrition_cache[name] = data
    time.sleep(0.5)

# ==========================================
# 2. ปรับปรุง: สร้างตารางโดยใช้ "ชื่อไทย" เท่านั้น
# ==========================================
final_rows = []
for thai_key, usda_val in USDA_MAP.items():
    if usda_val in nutrition_cache:
        cached_data = nutrition_cache[usda_val]
        
        # สร้าง row ใหม่ โดยตั้งชื่อคอลัมน์แรกว่า 'ingredient' เป็นชื่อไทย
        row = {'ingredient': thai_key}
        
        # กวาดเอาเฉพาะค่าสารอาหาร (ตัดชื่ออังกฤษ usda_name ทิ้ง)
        for k, v in cached_data.items():
            if k not in ['usda_name', 'match_name']: 
                row[k] = v
                
        final_rows.append(row)
    else:
        print(f"ไม่พบข้อมูลสำหรับ: {thai_key}")

# 3. บันทึกไฟล์
if final_rows:
    df_db = pd.DataFrame(final_rows)
    
    # จัดลำดับคอลัมน์ (เอา ingredient ขึ้นก่อนเสมอ)
    cols = ['ingredient'] + [c for c in df_db.columns if c != 'ingredient']
    df_db = df_db[cols]
    
    df_db.to_csv('thai_nutrition_db.csv', index=False)
    print("บันทึกไฟล์ฐานข้อมูล 'usda_nutrition_db.csv' เรียบร้อยครับ")
else:
    print("ไม่พบข้อมูลเลย โปรดตรวจสอบ API Key หรืออินเทอร์เน็ต")
