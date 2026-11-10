"""Kiểm tra & chuẩn hóa dữ liệu, tạo cột thời gian."""
import pandas as pd
import streamlit as st

NUM_COLS = ["line_count", "units", "subtotal", "tax_amount",
            "shipping_amount", "gross_payment", "refund_amount", "net_revenue"]
NOT_SOLD_STATUS = ["cancelled", "refunded"]


def quality_report(df: pd.DataFrame) -> dict:
    """Báo cáo chất lượng dữ liệu (không xóa gì, chỉ kiểm tra)."""
    return {
        "Số dòng": len(df),
        "Số ô thiếu": int(df.isna().sum().sum()),
        "order_id trùng": int(df["order_id"].duplicated().sum()),
        "Dòng trùng hoàn toàn": int(df.duplicated().sum()),
        "net_revenue <= 0": int((df["net_revenue"] <= 0).sum()),
        "net_revenue âm": int((df["net_revenue"] < 0).sum()),
    }


@st.cache_data(show_spinner="Đang làm sạch dữ liệu...")
def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    # ordered_at dạng "2025-05-09T16:24:59Z" -> datetime (bỏ timezone)
    df["ordered_at"] = pd.to_datetime(df["ordered_at"], errors="coerce", utc=True).dt.tz_localize(None)
    for c in NUM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["ordered_at"])  # chỉ bỏ dòng không có thời gian hợp lệ
    # Cột thời gian
    df["year"] = df["ordered_at"].dt.year
    df["month"] = df["ordered_at"].dt.month
    df["quarter"] = df["ordered_at"].dt.quarter
    df["date"] = df["ordered_at"].dt.normalize()
    # Cờ đơn bán thành công: net_revenue > 0 và không phải cancelled/refunded
    df["is_sale"] = (df["net_revenue"] > 0) & (~df["order_status"].isin(NOT_SOLD_STATUS))
    return df
