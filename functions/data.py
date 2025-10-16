import os
import pandas as pd
import streamlit as st

# Constants
DATA_PATH = "thai_food_processed_cleaned.csv"
LEGACY_DATA_PATH = "thai_food_processed.csv"

@st.cache_data
def load_food_data():
    """Load Thai food dataset, handling legacy column names."""
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
    elif os.path.exists(LEGACY_DATA_PATH):
        df = pd.read_csv(LEGACY_DATA_PATH)
    else:
        return pd.DataFrame()

    if 'text_ingradiant' in df.columns:
        df = df.rename(columns={'text_ingradiant': 'ingredient'})
    if 'food_method' in df.columns:
        df = df.rename(columns={'food_method': 'method'})
    return df


