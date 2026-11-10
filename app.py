"""Điểm vào của Dashboard: đọc dữ liệu -> bộ lọc chung -> điều hướng 5 Page."""
import streamlit as st
from utils.load_data import load_raw_data
from utils.clean_data import clean_data, quality_report
from utils.filters import sidebar_filters
from pages import (page1_overview, page2_sales_trend, page3_country_analysis,
                   page4_order_analysis, page5_customer_channel)

st.set_page_config(page_title="E-commerce Dashboard", page_icon="🛒", layout="wide")

try:
    raw = load_raw_data()
    df_all = clean_data(raw)
except Exception as e:  # hiển thị lỗi thân thiện
    st.error(f"Không đọc được dữ liệu: {e}")
    st.stop()

df = sidebar_filters(df_all)  # bộ lọc dùng chung cho mọi Page

with st.sidebar.expander("🧪 Chất lượng dữ liệu"):
    st.json(quality_report(raw))
    st.caption("Chỉ kiểm tra, không xóa dữ liệu. Tiền tệ không được xác định trong dữ liệu.")

pages = [
    ("Tổng quan kinh doanh", "📊", page1_overview.render, "overview"),
    ("Xu hướng doanh thu", "📈", page2_sales_trend.render, "trend"),
    ("Theo quốc gia", "🌍", page3_country_analysis.render, "country"),
    ("Giá trị & cơ cấu đơn hàng", "🧾", page4_order_analysis.render, "orders"),
    ("Khách hàng & kênh", "🎯", page5_customer_channel.render, "customer"),
]
nav = st.navigation([st.Page(lambda fn=fn: fn(df), title=t, icon=i, url_path=u, default=(u == "overview"))
                     for t, i, fn, u in pages])
nav.run()
