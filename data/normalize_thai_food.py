#CMD: python normalize_thai_food.py --input dataset.jsonl --outdir ./normalized_output

import argparse
import csv
import json
import os
import re
import uuid
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List

import pandas as pd
from pythainlp.tokenize import word_tokenize
from tqdm import tqdm
from datasets import load_dataset

# ถ้าเป็น dataset registered:
ds = load_dataset("pythainlp/thai_food_v1.0", split="train")

# ds เป็น Dataset object — แปลงเป็น list of dict หรือ iterate ได้
items = []
for ex in ds:
    # dataset อาจมีฟิลด์ name, text หรือ pageContent ตาม schema
    name = ex.get("name") or ex.get("title")
    text = ex.get("text") or ex.get("pageContent") or ex.get("content")
    items.append({"name": name, "text": text})
# จากนั้นส่ง items เข้า process_items() ของสคริปต์ normalize
process_items(items, outdir="./normalized_output")

# -----------------------
# Default mappings (ขยายได้ตามต้องการ)
# -----------------------

UNIT_MAP_DEFAULT = {
    # raw -> {"canonical":..., "type":"mass|volume|count", "factor": factor_to_base}
    # mass: base = grams (g)
    "กรัม": {"canonical": "g", "type": "mass", "factor": 1},
    "g": {"canonical": "g", "type": "mass", "factor": 1},
    "ก": {"canonical": "g", "type": "mass", "factor": 1},
    "กก": {"canonical": "g", "type": "mass", "factor": 1000},
    "กิโล": {"canonical": "g", "type": "mass", "factor": 1000},
    "kg": {"canonical": "g", "type": "mass", "factor": 1000},

    # volume: base = milliliter (ml)
    "มิลลิลิตร": {"canonical": "ml", "type": "volume", "factor": 1},
    "มล": {"canonical": "ml", "type": "volume", "factor": 1},
    "ml": {"canonical": "ml", "type": "volume", "factor": 1},
    "ลิตร": {"canonical": "ml", "type": "volume", "factor": 1000},
    "ltr": {"canonical": "ml", "type": "volume", "factor": 1000},
    "ล": {"canonical": "ml", "type": "volume", "factor": 1000},
    "ช้อนชา": {"canonical": "tsp", "type": "volume", "factor": 5},
    "ชต": {"canonical": "tsp", "type": "volume", "factor": 5},
    "ช้อนโต๊ะ": {"canonical": "tbsp", "type": "volume", "factor": 15},
    "ช้อน": {"canonical": "tbsp", "type": "volume", "factor": 15},
    "ช้อนโต": {"canonical": "tbsp", "type": "volume", "factor": 15},
    "ชต.": {"canonical": "tsp", "type": "volume", "factor": 5},
    "ชต.": {"canonical": "tsp", "type": "volume", "factor": 5},
    "ถ้วย": {"canonical": "cup", "type": "volume", "factor": 240},
    "ถ้วยตวง": {"canonical": "cup", "type": "volume", "factor": 240},

    # count / piece
    "ตัว": {"canonical": "piece", "type": "count", "factor": 1},
    "ชิ้น": {"canonical": "piece", "type": "count", "factor": 1},
    "เม็ด": {"canonical": "piece", "type": "count", "factor": 1},
    "กลีบ": {"canonical": "piece", "type": "count", "factor": 1},
    "ฝัก": {"canonical": "piece", "type": "count", "factor": 1},
}

# density: g per ml (ใช้เมื่อแปลง volume->mass)
DENSITY_DEFAULT = {
    "น้ำ": 1.0,
    "น้ำตาลทราย": 0.85,
    "น้ำมันพืช": 0.92,
    "แป้งสาลี": 0.53,
    "นมสด": 1.03,
    # เพิ่มรายการตามต้องการ
}

# per piece average weight (g per piece) for count-based items
PER_PIECE_DEFAULT = {
    "กุ้งนาง": 20.0,
    "ไข่ไก่": 50.0,
    "มันฝรั่ง": 150.0,  # example
    # เพิ่มรายการตามต้องการ
}

# -----------------------
# Helpers: number parsing (ไทย/อารบิก), fraction, word-numbers
# -----------------------

THAI_DIGITS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")

THAI_WORD_NUMBER = {
    "ศูนย์": 0, "หนึ่ง": 1, "หนึ่งหน่อย": 1, "หนึ่งลูก": 1, "สอง": 2, "สาม": 3, "สี่": 4,
    "ห้า": 5, "หก": 6, "เจ็ด": 7, "แปด": 8, "เก้า": 9, "สิบ": 10, "ยี่": 2,
    "ครึ่ง": 0.5, "ครึ่งหนึ่ง": 0.5
}

def thai_digits_to_arabic(s: str) -> str:
    return s.translate(THAI_DIGITS)

def parse_quantity_text(qtext: Optional[str]) -> Tuple[Optional[float], Optional[str]]:
    """
    Parse quantity text to float if possible.
    Returns (value_or_none, normalized_text_or_none)
    Supports arabic numbers, thai digits, fractions like "1/2" or "1 1/2", ranges "1-2" -> avg,
    and some thai words like 'ครึ่ง', 'หนึ่ง' (limited).
    """
    if not qtext:
        return None, None
    s = qtext.strip()
    s = thai_digits_to_arabic(s)
    s = s.replace(",", ".")
    s = s.replace(" ", " ")  # weird spaces

    # range like 1-2 or 1 – 2 -> take average
    m_range = re.match(r'^\s*(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*$', s)
    if m_range:
        a = float(m_range.group(1))
        b = float(m_range.group(2))
        return ( (a + b) / 2.0, f"{a}-{b}" )

    # mixed fraction: "1 1/2"
    m_mixed = re.match(r'^\s*(\d+)\s+(\d+)/(\d+)\s*$', s)
    if m_mixed:
        val = int(m_mixed.group(1)) + int(m_mixed.group(2)) / int(m_mixed.group(3))
        return val, s

    # simple fraction: "1/2"
    m_frac = re.match(r'^\s*(\d+)\s*/\s*(\d+)\s*$', s)
    if m_frac:
        val = int(m_frac.group(1)) / int(m_frac.group(2))
        return val, s

    # numeric
    m_num = re.match(r'^\s*(\d+(?:\.\d+)?)\s*$', s)
    if m_num:
        return float(m_num.group(1)), s

    # thai word like "ครึ่ง" or "หนึ่ง"
    s_low = s.lower()
    if s_low in THAI_WORD_NUMBER:
        return float(THAI_WORD_NUMBER[s_low]), s_low

    # Try to pick leading number in mixed text: "2ช้อนโต๊ะ" or "2 ชต."
    m_leading = re.match(r'^\s*([0-9]+(?:\.[0-9]+)?)(.*)$', s)
    if m_leading:
        try:
            return float(m_leading.group(1)), m_leading.group(1)
        except:
            pass

    return None, s  # cannot parse

# -----------------------
# Parsing text sections: name, ingredient(s), method, tags, etc.
# -----------------------

SECTION_KEYS = ["name", "ingredient", "ingredients", "method", "tags", "prep_time", "cook_time", "servings", "time"]

SECTION_PATTERN = re.compile(
    r'(?im)^(name|ingredient|ingredients|method|tags|prep_time|cook_time|servings|time)\s*:\s*'
)

def split_sections(page_text: str) -> Dict[str, str]:
    """
    Split by lines that start with key: (case-insensitive)
    fallback: return {"raw": page_text}
    """
    text = page_text or ""
    matches = list(SECTION_PATTERN.finditer(text))
    if not matches:
        return {"raw": text.strip()}

    sections = {}
    for i, m in enumerate(matches):
        key = m.group(1).lower()
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        content = text[start:end].strip()
        sections[key] = content
    return sections

# -----------------------
# Ingredient parsing
# -----------------------

BULLET_RE = re.compile(r'^[\-\*\u2022]\s*')

def split_ingredient_lines(ingredient_text: str) -> List[str]:
    if not ingredient_text:
        return []
    t = ingredient_text.replace('\r\n', '\n').replace('\r', '\n')
    lines = [ln.strip() for ln in re.split(r'\n', t) if ln.strip()]
    # if only one line and contains separators, try split bullets/semi-colon
    if len(lines) == 1:
        single = lines[0]
        # common separators
        parts = re.split(r'\s*[\-•;]\s*', single)
        if len(parts) > 1:
            lines = [p.strip() for p in parts if p.strip()]
        else:
            parts2 = re.split(r'\s*[,;]\s*', single)
            if len(parts2) > 1:
                lines = [p.strip() for p in parts2 if p.strip()]
    # remove leading bullets
    clean = [BULLET_RE.sub('', ln) for ln in lines]
    return clean

KNOWN_UNITS_LOWER = set([k.lower() for k in UNIT_MAP_DEFAULT.keys()])

def extract_note_and_core(raw_line: str) -> Tuple[str, Optional[str]]:
    """
    Pull parentheses or trailing comma note
    """
    note = None
    m = re.search(r'[\(\[](.+)[\)\]]\s*$', raw_line)
    if m:
        note = m.group(1).strip()
        core = raw_line[:m.start()].strip()
        return core, note
    # trailing comma
    if ',' in raw_line:
        parts = [p.strip() for p in raw_line.split(',')]
        if len(parts) > 1:
            return parts[0], ','.join(parts[1:])
    return raw_line, note

def detect_unit_and_item(rest: str) -> Tuple[Optional[str], str]:
    """
    Given rest (after removing leading quantity), try find unit (from known list) at start
    If not found, try last token as unit (rare)
    Return (unit_raw or None, item_text)
    """
    tokens = word_tokenize(rest, engine='newmm')
    if not tokens:
        return None, rest.strip()
    # check first two tokens and first token
    first_two = ' '.join(tokens[:2]).lower() if len(tokens) >= 2 else ''
    first_one = tokens[0].lower()
    if first_two in KNOWN_UNITS_LOWER:
        unit = first_two
        item = rest[len(first_two):].strip()
        return unit, item
    if first_one in KNOWN_UNITS_LOWER:
        unit = first_one
        item = rest[len(first_one):].strip()
        return unit, item
    # check token with punctuation stripped
    t0 = re.sub(r'\W+$', '', first_one)
    if t0 in KNOWN_UNITS_LOWER:
        unit = t0
        item = rest[len(first_one):].strip()
        return unit, item
    # fallback: maybe unit at end (e.g., "ไข่ไก่ 2 ฟอง" handled earlier) - return None
    return None, rest.strip()

def parse_ingredient_line(raw_line: str) -> Dict[str, Any]:
    """
    Return a dict with fields:
    raw, quantity, quantity_text, unit_raw, unit_canonical, unit_type, item, note, grams, ml
    """
    raw = raw_line.strip()
    core, note = extract_note_and_core(raw)
    # try to find leading quantity
    m_lead = re.match(r'^\s*([0-9๐-๙\/\.\,]+)\s*(.*)$', core)
    quantity = None
    qtext = None
    rest = core
    if m_lead:
        qraw = m_lead.group(1)
        rest = m_lead.group(2).strip()
        quantity, qtext = parse_quantity_text(qraw)
    else:
        # sometimes pattern is "4 ตัว กุ้ง" or "กุ้ง 4 ตัว", so try find number anywhere at start or end
        m_num_after = re.match(r'^(.*?)([0-9๐-๙\/\.\,]+)\s*([^\d].*)?$', core)
        # brute fallback: find first numeric substring
        m_anynum = re.search(r'([0-9๐-๙\/\.\,]+)', core)
        if m_anynum:
            # try to extract surrounding context to find unit after/before
            num_str = m_anynum.group(1)
            quantity, qtext = parse_quantity_text(num_str)
            # remove this number from core to help unit detection
            rest = (core[:m_anynum.start()] + core[m_anynum.end():]).strip()

    # detect unit and item
    unit_raw, item = detect_unit_and_item(rest)

    # If unit not detected and item starts with something like "ช้อนโต๊ะน้ำมัน" try to split letters
    if not unit_raw and rest:
        # look for unit token anywhere in rest tokens
        tokens = word_tokenize(rest, engine='newmm')
        for i, tk in enumerate(tokens):
            if tk.lower() in KNOWN_UNITS_LOWER:
                unit_raw = tk.lower()
                # rebuild item without that token
                tokens.pop(i)
                item = ''.join(tokens).strip()
                break

    item = item.strip() if item else None

    # Normalize unit via UNIT_MAP_DEFAULT (case-insensitive)
    unit_canonical = None
    unit_type = None
    grams = None
    ml = None
    if unit_raw:
        um = UNIT_MAP_DEFAULT.get(unit_raw) or UNIT_MAP_DEFAULT.get(unit_raw.lower())
        if um:
            unit_canonical = um["canonical"]
            unit_type = um["type"]
        else:
            # try strip punctuation / dots
            um = UNIT_MAP_DEFAULT.get(unit_raw.strip('.')) or UNIT_MAP_DEFAULT.get(unit_raw.lower().strip('.'))
            if um:
                unit_canonical = um["canonical"]
                unit_type = um["type"]

    # compute grams/ml if possible
    if quantity is not None and unit_canonical:
        um = UNIT_MAP_DEFAULT.get(unit_raw) or UNIT_MAP_DEFAULT.get(unit_raw.lower())
        if um:
            factor = um["factor"]
            if um["type"] == "mass":
                grams = float(quantity) * float(factor)
            elif um["type"] == "volume":
                ml = float(quantity) * float(factor)
                # try convert ml->g using density
                if item:
                    dens = DENSITY_DEFAULT.get(item)
                    if dens:
                        grams = ml * float(dens)
            elif um["type"] == "count":
                # multiply by per-piece weight if available
                if item:
                    avg = PER_PIECE_DEFAULT.get(item)
                    if avg:
                        grams = float(quantity) * float(avg)

    return {
        "raw": raw,
        "quantity": quantity,
        "quantity_text": qtext,
        "unit_raw": unit_raw,
        "unit_canonical": unit_canonical,
        "unit_type": unit_type,
        "item": item,
        "note": note,
        "grams": grams,
        "ml": ml
    }

# -----------------------
# Main processing pipeline
# -----------------------

def read_input_file(input_path: str) -> List[Dict[str, Any]]:
    """
    Support:
    - JSONL: one json per line
    - JSON array
    - CSV with columns 'name' and 'text' (or 'content')
    """
    ext = os.path.splitext(input_path)[1].lower()
    items = []
    if ext in (".jsonl", ".ndjson"):
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    items.append(obj)
                except Exception as e:
                    print("WARN: skip invalid json line:", e)
    elif ext == ".json":
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                # maybe dict of items
                # try to infer: if keys mapping to objects with name/text
                # else wrap
                items = [data]
    elif ext in (".csv", ".tsv"):
        sep = '\t' if ext == ".tsv" else ','
        df = pd.read_csv(input_path, sep=sep, dtype=str).fillna('')
        # expect columns name and text/content
        possible_text_cols = ['text', 'content', 'pageContent', 'raw_text']
        for _, row in df.iterrows():
            name = row.get('name') or row.get('title') or ''
            txt = ''
            for c in possible_text_cols:
                if c in row and row[c]:
                    txt = row[c]
                    break
            # if none found, try full row string
            if not txt:
                txt = ' '.join([str(x) for x in row.values if x])
            items.append({"name": name, "text": txt})
    else:
        # try read as text file: each paragraph as one item
        with open(input_path, "r", encoding="utf-8") as f:
            raw = f.read()
            parts = re.split(r'\n\s*\n+', raw)
            for p in parts:
                if p.strip():
                    items.append({"name": "", "text": p.strip()})
    return items

def process_items(items: List[Dict[str, Any]], outdir: str):
    recipes_rows = []
    ingredients_rows = []
    parse_log = []

    for rec_idx, obj in enumerate(tqdm(items, desc="Processing")):
        name = obj.get("name") or ""
        page_text = obj.get("text") or obj.get("pageContent") or ""
        sections = split_sections(page_text)
        name_detected = sections.get("name") or name or ""
        ingredients_text = sections.get("ingredient") or sections.get("ingredients") or ""
        method_text = sections.get("method") or sections.get("time") or ""
        tags_text = sections.get("tags") or ""
        prep_time = sections.get("prep_time") or None
        cook_time = sections.get("cook_time") or None
        servings = sections.get("servings") or None

        # build recipe row
        recipe_id = str(uuid.uuid4())
        slug = re.sub(r'\s+', '-', (name_detected or "recipe-" + recipe_id[:8]).strip()).lower()
        recipe_row = {
            "recipe_id": recipe_id,
            "name": name_detected.strip() if name_detected else None,
            "slug": slug,
            "raw_text": page_text,
            "method": method_text.strip() if method_text else None,
            "tags": tags_text.strip() if tags_text else None,
            "prep_time_minutes": int(prep_time) if prep_time and prep_time.isdigit() else None,
            "cook_time_minutes": int(cook_time) if cook_time and cook_time.isdigit() else None,
            "servings": int(servings) if servings and servings.isdigit() else None,
            "imported_at": datetime.utcnow().isoformat() + "Z",
        }
        recipes_rows.append(recipe_row)

        # parse ingredients
        ing_lines = split_ingredient_lines(ingredients_text)
        if not ing_lines:
            # heuristics: maybe ingredients embedded in text; try to find lines that look like ingredients
            # naive: find lines with numbers or units
            all_lines = [ln.strip() for ln in re.split(r'\n', page_text) if ln.strip()]
            cand = []
            for ln in all_lines:
                if re.search(r'\d', ln) or any(u in ln for u in ["ช้อน", "กรัม", "g", "ml", "ถ้วย", "ตัว", "ชิ้น"]):
                    cand.append(ln)
            if cand and len(cand) <= 30:
                ing_lines = cand

        for seq, ln in enumerate(ing_lines, start=1):
            parsed = parse_ingredient_line(ln)
            parsed_row = {
                "recipe_id": recipe_id,
                "seq": seq,
                "raw": parsed.get("raw"),
                "quantity": parsed.get("quantity"),
                "quantity_text": parsed.get("quantity_text"),
                "unit_raw": parsed.get("unit_raw"),
                "unit_canonical": parsed.get("unit_canonical"),
                "unit_type": parsed.get("unit_type"),
                "item": parsed.get("item"),
                "note": parsed.get("note"),
                "grams": parsed.get("grams"),
                "ml": parsed.get("ml"),
            }
            ingredients_rows.append(parsed_row)

            # logging if grams not computed but should be
            if parsed_row["grams"] is None:
                parse_log.append({
                    "recipe_id": recipe_id,
                    "seq": seq,
                    "raw": parsed_row["raw"],
                    "quantity": parsed_row["quantity"],
                    "unit_raw": parsed_row["unit_raw"],
                    "item": parsed_row["item"],
                    "reason": "no grams (missing density/per-piece or unparsable quantity/unit)"
                })

    # Save CSVs
    recipes_df = pd.DataFrame(recipes_rows)
    ingredients_df = pd.DataFrame(ingredients_rows)

    recipes_csv = os.path.join(outdir, "recipes.csv")
    ingredients_csv = os.path.join(outdir, "recipe_ingredients.csv")
    recipes_df.to_csv(recipes_csv, index=False, encoding="utf-8")
    ingredients_df.to_csv(ingredients_csv, index=False, encoding="utf-8")

    # Save default maps to outdir so user can edit/extend
    with open(os.path.join(outdir, "unit_map.json"), "w", encoding="utf-8") as f:
        json.dump(UNIT_MAP_DEFAULT, f, ensure_ascii=False, indent=2)
    with open(os.path.join(outdir, "density.json"), "w", encoding="utf-8") as f:
        json.dump(DENSITY_DEFAULT, f, ensure_ascii=False, indent=2)
    with open(os.path.join(outdir, "per_piece.json"), "w", encoding="utf-8") as f:
        json.dump(PER_PIECE_DEFAULT, f, ensure_ascii=False, indent=2)

    with open(os.path.join(outdir, "parse_log.json"), "w", encoding="utf-8") as f:
        json.dump(parse_log, f, ensure_ascii=False, indent=2)

    print("Saved:", recipes_csv, ingredients_csv)
    print("Saved mapping examples to:", os.path.join(outdir, "unit_map.json"))
    print("Saved parse log to:", os.path.join(outdir, "parse_log.json"))

# -----------------------
# CLI
# -----------------------

def main():
    parser = argparse.ArgumentParser(description="Normalize thai food dataset (name,text) to normalized CSVs")
    parser.add_argument("--input", "-i", required=True, help="Input file (jsonl, json, csv, txt). Expect fields: name, text")
    parser.add_argument("--outdir", "-o", required=True, help="Output directory to save CSVs and maps")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    print("Reading input:", args.input)
    items = read_input_file(args.input)
    print("Items loaded:", len(items))
    process_items(items, args.outdir)

if __name__ == "__main__":
    main()