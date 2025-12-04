import pandas as pd
import requests
import time

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
            'api_key': API_KEY, 'query': query_name, 'pageSize': 1,
            'dataType': ['Foundation', 'SR Legacy']
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

# เริ่มดึงข้อมูล
db_rows = []
print(f"กำลังสร้างฐานข้อมูลจาก {len(unique_usda_names)} รายการ...")

for i, name in enumerate(unique_usda_names):
    print(f"[{i+1}/{len(unique_usda_names)}] Fetching: {name}")
    data = fetch_per_100g(name)
    if data:
        # เติมค่า 0 ให้ครบทุกคอลัมน์ถ้า API ไม่ส่งมา
        for col in NUTRIENT_MAP.values():
            if col not in data: data[col] = 0.0
        db_rows.append(data)
    time.sleep(0.5)

# บันทึกเป็น Master DB (Per 100g)
df_db = pd.DataFrame(db_rows)
df_db.to_csv('usda_nutrition_db.csv', index=False)
print("บันทึกไฟล์ฐานข้อมูล 'usda_nutrition_db.csv' เรียบร้อยครับ")