import pandas as pd
import re
import os
import argparse
import numpy as np
from typing import List, Dict, Optional
import json
from datetime import datetime

def clean_text(text: str) -> str:
    """
    ทำความสะอาดและจัดรูปแบบข้อความ
    
    Args:
        text (str): ข้อความที่ต้องการทำความสะอาด
        
    Returns:
        str: ข้อความที่ทำความสะอาดแล้ว
    """
    if not isinstance(text, str):
        return ""
    
    # ลบช่องว่างที่เกินจำเป็น
    text = re.sub(r'\s+', ' ', text)
    
    # ลบอักขระพิเศษ ยกเว้นตัวอักษรไทย ตัวเลข และเครื่องหมายวรรคตอนพื้นฐาน
    text = re.sub(r'[^\u0E00-\u0E7Fa-zA-Z0-9\s.,\-\(\)\[\]/]', '', text)
    
    return text.strip()

def preprocess_ingredients(text: str) -> str:
    """
    จัดรูปแบบรายการวัตถุดิบให้เป็นมาตรฐาน
    
    Args:
        text (str): รายการวัตถุดิบ
        
    Returns:
        str: รายการวัตถุดิบที่จัดรูปแบบแล้ว
    """
    if not isinstance(text, str):
        return ""
    
    # แยกบรรทัด
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # ทำความสะอาดเครื่องหมายที่ไม่ต้องการ
        line = re.sub(r'^[-•*\s]+', '', line)  # ลบเครื่องหมาย bullet ที่หน้า
        
        # เพิ่มเครื่องหมาย dash ถ้ายังไม่มี
        if line and not line.startswith('- '):
            line = f"- {line}"
        
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def standardize_ingredient_amounts(text: str) -> str:
    """
    มาตรฐานปริมาณและหน่วยของวัตถุดิบ
    
    Args:
        text (str): ข้อความวัตถุดิบ
        
    Returns:
        str: ข้อความที่มีหน่วยมาตรฐาน
    """
    if not isinstance(text, str):
        return text
    
    # พจนานุกรมแปลงหน่วย
    unit_standardization = {
        'กิโลกรัม': 'กิโลกรัม', 'กก.': 'กิโลกรัม', 'กก': 'กิโลกรัม',
        'กรัม': 'กรัม', 'ก.': 'กรัม', 'ก': 'กรัม',
        'ช้อนโต๊ะ': 'ช้อนโต๊ะ', 'ช้อนใหญ่': 'ช้อนโต๊ะ', 
        'ช้อนชา': 'ช้อนชา', 'ช้อนเล็ก': 'ช้อนชา',
        'ถ้วยตวง': 'ถ้วยตวง', 'ถ้วย': 'ถ้วยตวง',
        'ลูก': 'ลูก', 'หัว': 'หัว', 'กิ่ง': 'กิ่ง',
        'แผ่น': 'แผ่น', 'เส้น': 'เส้น', 'ฝัก': 'ฝัก',
        'ใบ': 'ใบ', 'ดอก': 'ดอก'
    }
    
    # ประมาณปริมาณจากคำอธิบาย
    amount_estimation = {
        r'เล็กน้อย|นิดหน่อย|เล็กๆ': '1 ช้อนชา',
        r'ปานกลาง|กลาง|พอประมาณ': '1 ช้อนโต๊ะ',
        r'มาก|เยอะ|เยอะๆ|ใหญ่': '2 ช้อนโต๊ะ',
        r'ตามชอบ|ตามใจชอบ': '1 ช้อนชา',
        r'หยิบมือหนึ่ง|กำมือหนึ่ง': '30 กรัม'
    }
    
    processed_text = text
    
    # แทนที่หน่วยด้วยหน่วยมาตรฐาน
    for old_unit, new_unit in unit_standardization.items():
        processed_text = re.sub(rf'\b{old_unit}\b', new_unit, processed_text)
    
    # เพิ่มปริมาณประมาณสำหรับคำอธิบาย
    for pattern, replacement in amount_estimation.items():
        if re.search(pattern, processed_text) and not re.search(r'\d+', processed_text):
            processed_text = f"{replacement} {processed_text}"
            break
    
    return processed_text


def _parse_fraction(qty_str: str) -> float:
    """Parse simple fractions like '1/2' or decimal strings."""
    from fractions import Fraction
    qty_str = qty_str.strip()
    if '/' in qty_str:
        try:
            return float(Fraction(qty_str))
        except Exception:
            return 0.0
    try:
        return float(qty_str)
    except Exception:
        return 0.0


# Mapping units to grams (approximate for household measures)
UNIT_TO_GRAMS = {
    'กิโลกรัม': 1000.0,
    'กรัม': 1.0,
    'ช้อนโต๊ะ': 15.0,
    'ช้อนชา': 5.0,
    'ถ้วยตวง': 200.0,
    'ถ้วย': 200.0,
    'ลูก': 50.0,
    'หัว': 80.0,
    'กิ่ง': 10.0,
    'ฝัก': 10.0,
    'ใบ': 5.0,
    'ดอก': 10.0,
    'แผ่น': 5.0,
    'เส้น': 5.0
}


def convert_ingredient_line_to_grams(line: str, default_grams: float = 20.0) -> str:
    """Convert a single ingredient line to a grams-normalized line.

    Returns a string like '- 50 กรัม กุ้งสด' or leaves the ingredient with an estimated grams
    if no numeric quantity was present.
    """
    if not isinstance(line, str) or not line.strip():
        return line

    original = line.strip()
    # remove leading bullets
    clean = re.sub(r'^[-•*\s]+', '', original)

    # look for a numeric quantity (including fractions)
    # e.g., '1/2', '2.5', '3'
    qty_match = re.search(r'(?P<qty>\d+\s*/\s*\d+|\d+\.\d+|\d+)', clean)
    unit_match = None
    if qty_match:
        qty_str = qty_match.group('qty')
        qty = _parse_fraction(qty_str.replace(' ', ''))
        # after qty, try to find a unit word
        after = clean[qty_match.end():]
        unit_search = re.search(r'\b(กิโลกรัม|กรัม|ช้อนโต๊ะ|ช้อนชา|ถ้วยตวง|ถ้วย|ลูก|หัว|กิ่ง|ฝัก|ใบ|ดอก|แผ่น|เส้น)\b', after)
        if unit_search:
            unit = unit_search.group(1)
            grams = qty * UNIT_TO_GRAMS.get(unit, 1.0)
            # remove the matched qty+unit from text
            rest = (clean[:qty_match.start()] + clean[qty_match.end():]).strip()
            rest = re.sub(r'\b' + re.escape(unit) + r'\b', '', rest).strip()
            return f"- {int(round(grams))} กรัม {rest}".strip()
        else:
            # numeric present but no unit: assume grams
            grams = qty
            rest = (clean[:qty_match.start()] + clean[qty_match.end():]).strip()
            return f"- {int(round(grams))} กรัม {rest}".strip()
    else:
        # No numeric qty found; look for unit words only
        unit_only = re.search(r'\b(กิโลกรัม|กรัม|ช้อนโต๊ะ|ช้อนชา|ถ้วยตวง|ถ้วย|ลูก|หัว|กิ่ง|ฝัก|ใบ|ดอก|แผ่น|เส้น)\b', clean)
        if unit_only:
            unit = unit_only.group(1)
            grams = UNIT_TO_GRAMS.get(unit, default_grams)
            rest = re.sub(r'\b' + re.escape(unit) + r'\b', '', clean).strip()
            return f"- {int(round(grams))} กรัม {rest}".strip()
        # fallback: no qty or unit -> estimate small amount
        return f"- {int(round(default_grams))} กรัม {clean}".strip()


def convert_ingredient_block_to_grams(block: str) -> str:
    """Convert a block of ingredient lines (separated by newline) to grams-normalized lines."""
    if not isinstance(block, str):
        return block
    lines = [ln for ln in block.split('\n') if ln.strip()]
    converted = [convert_ingredient_line_to_grams(ln) for ln in lines]
    return '\n'.join(converted)

def extract_cooking_methods(text: str) -> List[str]:
    """
    สกัดวิธีการทำอาหารจากข้อความ
    
    Args:
        text (str): ข้อความวิธีทำ
        
    Returns:
        List[str]: รายการวิธีการทำอาหาร
    """
    if not isinstance(text, str):
        return []
    
    cooking_methods = []
    method_keywords = {
        'ทอด': ['ทอด', 'ลงกระทะ', 'น้ำมันร้อน'],
        'ผัด': ['ผัด', 'คนให้เข้ากัน'],
        'ต้ม': ['ต้ม', 'เอาไปต้ม', 'ใส่น้ำ'],
        'นึ่ง': ['นึ่ง', 'หม้อนึ่ง'],
        'ปิ้ง': ['ปิ้ง', 'ย่าง'],
        'คั่ว': ['คั่ว', 'คั่วให้หอม'],
        'ดอง': ['ดอง', 'หมัก'],
        'ต้มแกง': ['แกง', 'ใส่กะทิ']
    }
    
    for method, keywords in method_keywords.items():
        if any(keyword in text for keyword in keywords):
            cooking_methods.append(method)
    
    return cooking_methods if cooking_methods else ['ผสม']  # default method

def validate_recipe_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    ตรวจสอบและทำความสะอาดข้อมูลสูตรอาหาร
    
    Args:
        df (pd.DataFrame): ข้อมูลสูตรอาหารดิบ
        
    Returns:
        pd.DataFrame: ข้อมูลที่ตรวจสอบและทำความสะอาดแล้ว
    """
    # ลบแถวที่ข้อมูลสำคัญว่าง
    df = df.dropna(subset=['name'])
    
    # เติมข้อมูลที่หายไป
    df['text_ingradiant'] = df['text_ingradiant'].fillna('- ไม่ระบุวัตถุดิบ')
    df['food_method'] = df['food_method'].fillna('ไม่ระบุวิธีทำ')
    
    # ตรวจสอบความยาวของข้อมูล
    df = df[df['name'].str.len() >= 2]  # ชื่ออาหารต้องมีความยาวอย่างน้อย 2 ตัวอักษร
    
    # ลบรายการซ้ำ (เก็บรายการแรก)
    df = df.drop_duplicates(subset=['name'], keep='first')
    
    return df

def enhance_recipe_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    เพิ่มข้อมูลเพิ่มเติมให้กับสูตรอาหาร
    
    Args:
        df (pd.DataFrame): ข้อมูลสูตรอาหาร
        
    Returns:
        pd.DataFrame: ข้อมูลที่เพิ่มเติมแล้ว
    """
    # เพิ่มคอลัมน์ข้อมูลเพิ่มเติม
    df['ingredient_count'] = df['text_ingradiant'].apply(
        lambda x: len([line for line in str(x).split('\n') if line.strip()])
    )
    
    df['cooking_methods'] = df['food_method'].apply(extract_cooking_methods)
    df['cooking_methods_str'] = df['cooking_methods'].apply(lambda x: ', '.join(x))
    
    # ประเมินความซับซ้อนของสูตร
    def estimate_complexity(row):
        ingredient_count = row['ingredient_count']
        method_text = str(row['food_method'])
        method_length = len(method_text)
        
        if ingredient_count <= 3 and method_length <= 100:
            return 'ง่าย'
        elif ingredient_count <= 7 and method_length <= 300:
            return 'ปานกลาง'
        else:
            return 'ยาก'
    
    df['complexity'] = df.apply(estimate_complexity, axis=1)
    
    # เพิ่มแท็กหมวดหมู่อาหาร
    def categorize_food(name):
        name_lower = name.lower()
        
        if any(word in name_lower for word in ['แกง', 'ต้มยำ', 'ต้มข่า']):
            return 'แกงและซุป'
        elif any(word in name_lower for word in ['ผัด', 'ผัดไท', 'ผัดกะเพรา']):
            return 'อาหารผัด'
        elif any(word in name_lower for word in ['ทอด', 'ปอเปี๊ยะ']):
            return 'อาหารทอด'
        elif any(word in name_lower for word in ['ยำ', 'ตำ', 'ลาบ']):
            return 'ยำและตำ'
        elif any(word in name_lower for word in ['ข้าว', 'เสี้ยว', 'ก๋วยเตี๋ยว']):
            return 'อาหารหลัก'
        elif any(word in name_lower for word in ['ขนม', 'เค้ก', 'ลูกชุบ']):
            return 'ขนมและของหวาน'
        else:
            return 'อื่นๆ'
    
    df['category'] = df['name'].apply(categorize_food)
    
    # แปลงหน่วยวัตถุดิบทั้งหมดเป็นกรัม (ทดลองด้วยการประมาณ)
    df['text_ingradiant_grams'] = df['text_ingradiant'].apply(convert_ingredient_block_to_grams)

    # เพิ่มคอลัมน์ dish_type: 'จานเดียว' หรือ 'กับข้าว'
    def detect_dish_type(name, methods, category):
        name_l = name.lower()
        # heuristic rules
        if any(word in name_l for word in ['ข้าว', 'ก๋วยเตี๋ยว', 'ราเมง', 'ผัดไท', 'กระเพรา']):
            return 'จานเดียว'
        if category in ['แกงและซุป', 'อาหารผัด', 'อาหารทอด', 'ยำและตำ', 'อาหารหลัก']:
            return 'กับข้าว'
        # method-based heuristics
        if 'ต้ม' in methods or 'แกง' in methods:
            return 'กับข้าว'
        return 'จานเดียว'

    df['dish_type'] = df.apply(lambda r: detect_dish_type(r['name'], r.get('cooking_methods_str', ''), r.get('category', '')), axis=1)
    
    return df

def create_metadata_file(df: pd.DataFrame, output_path: str) -> None:
    """
    สร้างไฟล์ metadata สำหรับชุดข้อมูล
    
    Args:
        df (pd.DataFrame): ข้อมูลที่ประมวลผลแล้ว
        output_path (str): พาธไฟล์ output
    """
    metadata = {
        'dataset_info': {
            'name': 'Thai Food Recipes Dataset',
            'version': '2.0',
            'created_date': datetime.now().isoformat(),
            'total_recipes': len(df),
            'columns': list(df.columns),
            'categories': df['category'].value_counts().to_dict() if 'category' in df.columns else {},
            'complexity_distribution': df['complexity'].value_counts().to_dict() if 'complexity' in df.columns else {}
        },
        'preprocessing_info': {
            'text_cleaning': 'Applied',
            'ingredient_standardization': 'Applied',
            'duplicate_removal': 'Applied',
            'data_validation': 'Applied'
        },
        'statistics': {
            'avg_ingredient_count': float(df['ingredient_count'].mean()) if 'ingredient_count' in df.columns else 0,
            'max_ingredient_count': int(df['ingredient_count'].max()) if 'ingredient_count' in df.columns else 0,
            'min_ingredient_count': int(df['ingredient_count'].min()) if 'ingredient_count' in df.columns else 0
        }
    }
    
    # บันทึกไฟล์ metadata
    metadata_path = output_path.replace('.csv', '_metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"Metadata saved to: {metadata_path}")

def preprocess_data(input_file: str, output_file: str, enhanced_mode: bool = True) -> bool:
    """
    ประมวลผลข้อมูลอาหารไทยแบบครบถ้วน
    
    Args:
        input_file (str): ไฟล์ข้อมูลดิบ
        output_file (str): ไฟล์ข้อมูลที่ประมวลผลแล้ว
        enhanced_mode (bool): โหมดเพิ่มข้อมูลเพิ่มเติม
        
    Returns:
        bool: ความสำเร็จของการประมวลผล
    """
    # ตรวจสอบไฟล์อินพุต
    if not os.path.exists(input_file):
        print(f"Error: ไม่พบไฟล์อินพุต '{input_file}'")
        return False
    
    try:
        print("กำลังโหลดข้อมูล...")
        # โหลดข้อมูล
        df = pd.read_csv(input_file, encoding='utf-8')
        print(f"โหลดข้อมูลสำเร็จ: {len(df)} แถว")
        
        # ตรวจสอบคอลัมน์ที่จำเป็น
        required_columns = ['name', 'text_ingradiant', 'food_method']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Error: ไม่พบคอลัมน์ที่จำเป็น: {', '.join(missing_columns)}")
            return False
        
        print("กำลังทำความสะอาดข้อมูล...")
        # ทำความสะอาดข้อมูลพื้นฐาน
        df['name'] = df['name'].apply(clean_text)
        df['food_method'] = df['food_method'].apply(clean_text)
        df['text_ingradiant'] = df['text_ingradiant'].apply(preprocess_ingredients)
        
        # มาตรฐานวัตถุดิบ
        print("กำลังมาตรฐานวัตถุดิบ...")
        df['text_ingradiant'] = df['text_ingradiant'].apply(standardize_ingredient_amounts)
        
        # ตรวจสอบและทำความสะอาดข้อมูล
        print("กำลังตรวจสอบข้อมูล...")
        original_count = len(df)
        df = validate_recipe_data(df)
        removed_count = original_count - len(df)
        
        if removed_count > 0:
            print(f"ลบข้อมูลที่ไม่สมบูรณ์: {removed_count} แถว")
        
        # เพิ่มข้อมูลเพิ่มเติม (ถ้าเปิดใช้งาน)
        if enhanced_mode:
            print("กำลังเพิ่มข้อมูลเพิ่มเติม...")
            df = enhance_recipe_data(df)
        
        # รีเซ็ตอินเด็กซ์
        df = df.reset_index(drop=True)
        
        # บันทึกข้อมูลที่ประมวลผลแล้ว
        print("กำลังบันทึกไฟล์...")
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        # สร้างไฟล์ metadata
        if enhanced_mode:
            create_metadata_file(df, output_file)
        
        print(f"ประมวลผลสำเร็จ! บันทึกไปที่ '{output_file}'")
        print(f"จำนวนสูตรอาหารทั้งหมด: {len(df)}")
        
        # แสดงสถิติเพิ่มเติม
        if enhanced_mode and 'category' in df.columns:
            print("\nสถิติหมวดหมู่อาหาร:")
            category_counts = df['category'].value_counts()
            for category, count in category_counts.items():
                print(f"  - {category}: {count} รายการ")
        
        # ลบไฟล์ embeddings เก่า (ถ้ามี) เพื่อให้สร้างใหม่
        embeddings_files = ['embeddings.pkl', 'recipe_embeddings.pkl']
        for emb_file in embeddings_files:
            if os.path.exists(emb_file):
                os.remove(emb_file)
                print(f"ลบไฟล์ embeddings เก่า: {emb_file}")
        
        return True
        
    except Exception as e:
        print(f"Error: เกิดข้อผิดพลาดในการประมวลผล: {str(e)}")
        return False

def main():
    """ฟังก์ชันหลักสำหรับรันสคริปต์"""
    parser = argparse.ArgumentParser(
        description='สคริปต์ประมวลผลข้อมูลสูตรอาหารไทย (Thai Food Recipe Preprocessor)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ตัวอย่างการใช้งาน:
  python preprocess.py --input thai_food_raw.csv --output thai_food_processed_cleaned.csv
  python preprocess.py --input data.csv --output clean_data.csv --enhanced
  python preprocess.py --input data.csv --output basic_data.csv --no-enhanced
        """
    )
    
    parser.add_argument(
        '--input', '-i', 
        type=str, 
        default='thai_food_raw.csv',
        help='ไฟล์อินพุต CSV (default: thai_food_raw.csv)'
    )
    
    parser.add_argument(
        '--output', '-o', 
        type=str, 
        default='thai_food_processed_cleaned.csv',
        help='ไฟล์เอาต์พุต CSV (default: thai_food_processed_cleaned.csv)'
    )
    
    parser.add_argument(
        '--enhanced', 
        action='store_true',
        help='เปิดใช้โหมดเพิ่มข้อมูลเพิ่มเติม (หมวดหมู่, ความซับซ้อน, etc.)'
    )
    
    parser.add_argument(
        '--no-enhanced', 
        action='store_true',
        help='ปิดใช้โหมดเพิ่มข้อมูลเพิ่มเติม (ทำความสะอาดพื้นฐานเท่านั้น)'
    )
    
    args = parser.parse_args()
    
    # กำหนดโหมด enhanced
    if args.no_enhanced:
        enhanced_mode = False
    elif args.enhanced:
        enhanced_mode = True
    else:
        enhanced_mode = True  # default เป็น enhanced
    
    print("=" * 60)
    print("🍲 Thai Food Recipe Preprocessor 🍲")
    print("=" * 60)
    print(f"Input file: {args.input}")
    print(f"Output file: {args.output}")
    print(f"Enhanced mode: {'✅ เปิดใช้งาน' if enhanced_mode else '❌ ปิดใช้งาน'}")
    print("-" * 60)
    
    # เริ่มประมวลผล
    success = preprocess_data(args.input, args.output, enhanced_mode)
    
    if success:
        print("\n✅ ประมวลผลสำเร็จ!")
        print("🚀 พร้อมใช้งานกับแอปพลิเคชัน Thai Food Nutrition Analyzer")
    else:
        print("\n❌ ประมวลผลล้มเหลว!")
        print("🔧 กรุณาตรวจสอบไฟล์อินพุตและลองใหม่")

if __name__ == "__main__":
    main()
