import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- 1. CONFIGURATION ---
# TODO: ใส่ API Key ที่ได้รับจาก USDA ที่นี่
API_KEY = os.getenv("USDA_API_KEY")
API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# รายการวัตถุดิบ (ภาษาอังกฤษ) สำหรับสร้างฐานข้อมูลโภชนาการหลัก
# คุณสามารถเพิ่มเติมรายการที่ต้องการได้ที่นี่
INGREDIENT_SEARCH_TERMS = [
    # Meats & Seafood
    "Chicken breast, raw", "Pork loin, raw", "Beef sirloin, raw", "Shrimp, raw", "Fish, tilapia, raw",
    "Squid, raw", "Mussels, raw", "Crab meat, canned", "Dried shrimp",

    # Vegetables
    "Holy basil", "Sweet basil", "Galangal, raw", "Lemongrass, raw", "Kaffir lime leaves",
    "Chili pepper, red, raw", "Garlic, raw", "Shallots, raw", "Onion, raw", "Tomato, raw",
    "Yardlong bean, raw", "Thai eggplant, raw", "Cucumber, raw", "Papaya, green, raw", "Mushroom, straw, raw",
    "Bean sprouts, raw", "Coriander (Cilantro), raw", "Spring onion",

    # Fruits
    "Lime, raw", "Coconut milk, canned", "Tamarind paste", "Pineapple, raw", "Mango, raw",

    # Grains & Noodles
    "Jasmine rice, uncooked", "Rice noodles, dry", "Glass noodles, dry",

    # Sauces & Pastes
    "Fish sauce", "Oyster sauce", "Soy sauce, light", "Chili paste in oil",
    "Red curry paste", "Green curry paste",

    # Others
    "Palm sugar", "Peanuts, raw", "Tofu, firm", "Egg, whole, raw"
]

# ID ของสารอาหารที่ต้องการจาก API (ต่อ 100g)
NUTRIENT_IDS = {
    'calories': 1008,      # Energy (kcal)
    'protein': 1003,       # Protein (g)
    'fat': 1004,           # Total lipid (fat) (g)
    'carbs': 1005,         # Carbohydrate, by difference (g)
    'fiber': 1079,         # Fiber, total dietary (g)
    'sugar': 2000,         # Sugars, total including NLEA (g)
    'sodium': 1093         # Sodium, Na (mg)
}

OUTPUT_CSV_PATH = "usda_nutrition_database_full.csv"

# --- 2. FETCHING & PROCESSING LOGIC ---

def fetch_nutrition_data(ingredient_list):
    """
    ดึงข้อมูลโภชนาการสำหรับแต่ละวัตถุดิบจาก USDA API
    """
    nutrition_data = []

    for ingredient in ingredient_list:
        print(f"กำลังค้นหา: {ingredient}...")

        # The USDA FDC search endpoint expects the API key as a query parameter
        # (or in the URL). When using POST with a JSON body, put the API key in
        # the query string via `params=` and send the search body as JSON.
        payload = {
            "query": ingredient,
            "dataType": ["SR Legacy", "Foundation"],
            "pageSize": 50  # ดึงข้อมูลสูงสุด 50 รายการต่อคำค้นหา
        }

        try:
            # Send API key in query params, body in JSON
            resp = requests.post(API_URL, params={"api_key": API_KEY}, json=payload, timeout=30)
            # Debug: show the final request URL and body for diagnosis
            try:
                req_url = resp.request.url
            except Exception:
                req_url = API_URL
            print(f"  -> Request URL: {req_url}")
            print(f"  -> Request body (json): {payload}")

            resp.raise_for_status()
            data = resp.json()

            foods_found = data.get('foods', [])
            if not foods_found:
                print(f"  -> ⚠️ ไม่พบข้อมูลสำหรับ '{ingredient}'")
                continue

            print(f"  -> ✅ พบ {len(foods_found)} รายการสำหรับ '{ingredient}'. กำลังประมวลผล...")

            for food_item in foods_found:
                # ใช้ description จาก API เป็นชื่อหลักเพื่อความแม่นยำ
                description = food_item.get('description', 'N/A')
                
                record = {
                    'search_term': ingredient, # เก็บคำค้นหาเดิมไว้อ้างอิง
                    'ingredient_name': description
                }
                
                # Build a robust mapping of nutrientId -> value/amount
                food_nutrients = {}
                for n in food_item.get('foodNutrients', []):
                    if not isinstance(n, dict):
                        continue
                    # try multiple locations for the nutrient id
                    nid = None
                    if 'nutrientId' in n:
                        nid = n.get('nutrientId')
                    else:
                        nutrient_obj = n.get('nutrient') or {}
                        nid = nutrient_obj.get('id') or nutrient_obj.get('nutrientId')

                    # try multiple locations for the numeric value
                    if 'value' in n:
                        val = n.get('value')
                    elif 'amount' in n:
                        val = n.get('amount')
                    else:
                        val = (n.get('nutrient') or {}).get('amount')

                    if nid is None:
                        # unexpected shape; skip but log for debugging
                        print(f"    -> Warning: nutrient entry missing id: {n}")
                        continue

                    # normalize id to int when possible
                    try:
                        nid_key = int(nid)
                    except Exception:
                        nid_key = nid

                    try:
                        food_nutrients[nid_key] = float(val) if val is not None else 0.0
                    except Exception:
                        # fallback: store raw value
                        food_nutrients[nid_key] = val if val is not None else 0

                for name, nutrient_id in NUTRIENT_IDS.items():
                    record[name] = food_nutrients.get(nutrient_id, 0)

                nutrition_data.append(record)

            # หน่วงเวลา 1 วินาทีเพื่อไม่ให้ยิง API เร็วเกินไป
            time.sleep(1)

        except requests.exceptions.RequestException as e:
            # If we got a response object, include status/text for debugging
            if 'resp' in locals():
                try:
                    print(f"  -> ❌ API responded: {resp.status_code} - {resp.text}")
                except Exception:
                    pass
            print(f"  -> ❌ เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
            continue

    return nutrition_data

# --- 3. MAIN EXECUTION ---

if __name__ == "__main__":
    if API_KEY == "YOUR_API_KEY_HERE" or not API_KEY:
        print("="*50)
        print("🚨 ข้อผิดพลาด: กรุณาใส่ USDA API Key ของคุณในตัวแปร API_KEY")
        print("ไปที่: https://fdc.nal.usda.gov/api-key-signup.html เพื่อขอ API Key")
        print("="*50)
    else:
        print("🚀 เริ่มกระบวนการสร้างฐานข้อมูลโภชนาการ...")

        all_data = fetch_nutrition_data(INGREDIENT_SEARCH_TERMS)

        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8-sig')

            print("\n" + "="*50)
            print(f"🎉 บันทึกข้อมูลสำเร็จ! สร้างไฟล์ '{OUTPUT_CSV_PATH}' ที่มี {len(df)} รายการ")
            print("คุณสามารถใช้ไฟล์นี้เป็นฐานข้อมูลหลักในแอปพลิเคชันของคุณได้")
            print("="*50)
            print("\nตัวอย่างข้อมูล:")
            print(df.head())
        else:
            print("\n" + "="*50)
            print("ไม่สามารถดึงข้อมูลใดๆ ได้ กรุณาตรวจสอบ API Key หรือการเชื่อมต่ออินเทอร์เน็ต")
            print("="*50)

