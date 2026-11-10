"""Đọc dữ liệu Excel (có cache)."""
import os
import pandas as pd
import streamlit as st

FILE_NAME = "ecommerce-sales-v1.0.0-analysis.xlsx"
SHEET_NAME = "Ecommerce Sales & Returns Datas"


@st.cache_data(show_spinner="Đang đọc dữ liệu Excel...")
def load_raw_data() -> pd.DataFrame:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, FILE_NAME)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Không tìm thấy file: {path}")
    return pd.read_excel(path, sheet_name=SHEET_NAME, engine="openpyxl")
