import pandas as pd
import os
from preprocess import convert_ingredient_block_to_grams

INPUT = 'thai_food_processed.csv'
OUTPUT = 'thai_food_processed_with_grams.csv'

# heuristics for dish type
def detect_dish_type(name, methods, category):
    name_l = str(name).lower()
    methods_s = str(methods)
    if any(word in name_l for word in ['ข้าว', 'ก๋วยเตี๋ยว', 'ราเมง', 'ผัดไท', 'กระเพรา']):
        return 'จานเดียว'
    if category in ['แกงและซุป', 'อาหารผัด', 'อาหารทอด', 'ยำและตำ', 'อาหารหลัก']:
        return 'กับข้าว'
    if 'ต้ม' in methods_s or 'แกง' in methods_s:
        return 'กับข้าว'
    return 'จานเดียว'


def main():
    if not os.path.exists(INPUT):
        print(f'Input file not found: {INPUT}')
        return
    df = pd.read_csv(INPUT, encoding='utf-8')
    # detect ingredient and method columns
    if 'text_ingradiant' in df.columns:
        ing_col = 'text_ingradiant'
    elif 'ingredient' in df.columns:
        ing_col = 'ingredient'
    else:
        print('No ingredient column found (text_ingradiant or ingredient).')
        return

    if 'food_method' in df.columns:
        method_col = 'food_method'
    elif 'method' in df.columns:
        method_col = 'method'
    else:
        method_col = None

    # Create grams column named 'ingredient_grams' and keep original 'ingredient'
    df['ingredient_grams'] = df[ing_col].fillna('').apply(convert_ingredient_block_to_grams)

    # category may not exist; create placeholder
    if 'category' not in df.columns:
        df['category'] = ''

    df['dish_type'] = df.apply(lambda r: detect_dish_type(r.get('name',''), r.get(method_col, ''), r.get('category','')), axis=1)

    df.to_csv(OUTPUT, index=False, encoding='utf-8-sig')
    print(f'Wrote output to {OUTPUT}')

if __name__ == '__main__':
    main()
