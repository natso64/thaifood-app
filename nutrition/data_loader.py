"""
nutrition/data_loader.py
โหลดข้อมูลโภชนาการ
"""

import pandas as pd
import streamlit as st
from config import NUTRITION_CSV


@st.cache_data
def load_nutrition_data(filepath: str = NUTRITION_CSV) -> pd.DataFrame:
    """โหลดข้อมูลโภชนาการจาก CSV"""
    try:
        df = pd.read_csv(filepath)
        required_cols = ['ingredient', 'calories', 'protein', 'carbs', 'fat']
        
        if not all(col in df.columns for col in required_cols):
            st.error(f"CSV ต้องมี columns: {required_cols}")
            return pd.DataFrame()
        
        df['ingredient_lower'] = df['ingredient'].str.lower().str.strip()
        return df
    
    except FileNotFoundError:
        st.warning(f"ไม่พบไฟล์ {filepath}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading nutrition data: {e}")
        return pd.DataFrame()