import streamlit as st
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import json
import re
from typing import Dict

# --- Model and Tokenizer Loading ---
@st.cache_resource
def load_phi3_model_and_tokenizer():
    """
    Loads the Phi-3 model and tokenizer from Hugging Face.
    Caches the resources to avoid reloading on every run.
    """
    model_id = "microsoft/Phi-3-mini-4k-instruct"
    
    # Check for GPU availability, otherwise use CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    try:
        with st.spinner(f"กำลังโหลดโมเดล Phi-3 ({model_id}) บน {device}..."):
            model = AutoModelForCausalLM.from_pretrained(
                model_id, 
                device_map=device, 
                torch_dtype="auto", 
                trust_remote_code=True, 
            )
            tokenizer = AutoTokenizer.from_pretrained(model_id)
        return model, tokenizer
    except Exception as e:
        st.error(f"ไม่สามารถโหลดโมเดล Phi-3 ได้: {e}")
        return None, None

# Keep global placeholders; load lazily to avoid heavy work at import time
PHI3_MODEL = None
PHI3_TOKENIZER = None

def _ensure_phi3_loaded():
    """Load the model and tokenizer on first use and set globals."""
    global PHI3_MODEL, PHI3_TOKENIZER
    if PHI3_MODEL is None or PHI3_TOKENIZER is None:
        PHI3_MODEL, PHI3_TOKENIZER = load_phi3_model_and_tokenizer()


def run_phi3_inference(prompt: str, max_new_tokens: int = 256) -> str:
    """
    Runs inference using the loaded Phi-3 model.
    """
    # Ensure model/tokenizer available (lazy load)
    _ensure_phi3_loaded()
    if not PHI3_MODEL or not PHI3_TOKENIZER:
        return "ขออภัยค่ะ, โมเดล Phi-3 ไม่พร้อมใช้งานในขณะนี้"

    try:
        pipe = pipeline(
            "text-generation",
            model=PHI3_MODEL,
            tokenizer=PHI3_TOKENIZER,
        )
    except Exception as e:
        return f"ไม่สามารถสร้าง pipeline โมเดลได้: {e}"

    generation_args = {
        "max_new_tokens": max_new_tokens,
        "return_full_text": False,
        "temperature": 0.1,
        "do_sample": True,
    }
    
    # Format the prompt for Phi-3
    messages = [{"role": "user", "content": prompt}]
    formatted_prompt = PHI3_TOKENIZER.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    try:
        with st.spinner("AI กำลังประมวลผล..."):
            output = pipe(formatted_prompt, **generation_args)
        if output and isinstance(output, list) and 'generated_text' in output[0]:
            return output[0]['generated_text']
        return "ไม่สามารถสร้างคำตอบได้"
    except Exception as e:
        return f"เกิดข้อผิดพลาดระหว่างการประมวลผล: {e}"

def analyze_query_with_phi3(user_input: str) -> Dict:
    """
    ใช้ Phi-3 วิเคราะห์เจตนาของผู้ใช้และคืนค่าเป็น JSON.
    - type: 'menu', 'ingredients', หรือ 'other'
    - query: ข้อความที่ควรใช้ในการค้นหาต่อไป
    """
    prompt = f"""
    คุณคือผู้ช่วยวิเคราะห์คำค้นหาอาหาร วิเคราะห์เจตนาของผู้ใช้จากข้อความต่อไปนี้
    แล้วตอบกลับเป็น JSON object เท่านั้น ห้ามมีข้อความอื่นนอกเหนือจาก JSON

    - ถ้าผู้ใช้ต้องการค้นหาจาก "ชื่อเมนู" ให้ type เป็น "menu" และ query เป็นชื่อเมนูนั้น
    - ถ้าผู้ใช้ต้องการค้นหาจาก "วัตถุดิบ" ให้ type เป็น "ingredients" และ query เป็นรายการวัตถุดิบที่แยกด้วยจุลภาค
    - ถ้าไม่แน่ใจ ให้ type เป็น "other" และ query เป็นข้อความเดิม

    ตัวอย่าง:
    Input: "หาสูตรต้มยำกุ้งหน่อย"
    Output: {{"type": "menu", "query": "ต้มยำกุ้ง"}}

    Input: "มีไก่กับกะทิทำอะไรได้บ้าง"
    Output: {{"type": "ingredients", "query": "ไก่, กะทิ"}}

    Input: "ทำยังไงให้อร่อย"
    Output: {{"type": "other", "query": "ทำยังไงให้อร่อย"}}

    ---
    ข้อความจากผู้ใช้: "{user_input}"
    ---
    JSON Output:
    """
    
    content = run_phi3_inference(prompt, max_new_tokens=100)
    
    # พยายามแยก JSON ออกจากข้อความที่ LLM อาจจะสร้างเกินมา
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass # Fallback if JSON is invalid
    
    # Fallback ถ้าหา JSON ไม่เจอ
    return {"type": "other", "query": user_input}


def generate_recipe_chat_response(question: str, context: str):
    """
    Generates a recipe-related response using the local Phi-3 model.
    """
    # This prompt is crucial for guiding the LLM to use only the provided information.
    prompt = f"""
    คุณคือผู้ช่วยเชฟ AI ที่เป็นมิตรและเชี่ยวชาญ จงตอบคำถามของผู้ใช้โดยอ้างอิงจาก "ข้อมูลสูตรอาหาร" ที่ให้มาเท่านั้น
    ห้ามเพิ่มเติมข้อมูลที่ไม่มีอยู่ในสูตรเด็ดขาด และตอบเป็นภาษาไทยที่กระชับ เข้าใจง่าย

    ---
    [ข้อมูลสูตรอาหาร]
    {context}
    ---

    [คำถามจากผู้ใช้]
    "{question}"

    [คำตอบของคุณ]
    """

    return run_phi3_inference(prompt, max_new_tokens=512)
