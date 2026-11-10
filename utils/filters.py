"""Bộ lọc chung ở Sidebar, dùng cho cả 5 Page."""
import streamlit as st
import pandas as pd

MONTHS = list(range(1, 13))
QUARTERS = [1, 2, 3, 4]
_MULTI = [("f_countries", "country_code", "Quốc gia"),
          ("f_status", "order_status", "Trạng thái đơn hàng"),
          ("f_channels", "acquisition_channel", "Kênh tiếp cận"),
          ("f_segments", "customer_segment", "Phân khúc khách hàng")]


def _reset(df: pd.DataFrame):
    """Callback đặt lại bộ lọc về mặc định (toàn bộ 2023-2025)."""
    ss = st.session_state
    ss["f_all_years"] = True
    ss["f_years"] = sorted(df["year"].unique())
    ss["f_months"] = MONTHS
    ss["f_quarters"] = QUARTERS
    ss["f_dates"] = (df["date"].min().date(), df["date"].max().date())
    for key, col, _ in _MULTI:
        ss[key] = sorted(df[col].dropna().unique())


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Vẽ bộ lọc ở Sidebar và trả về DataFrame đã lọc."""
    years = sorted(df["year"].unique())
    dmin, dmax = df["date"].min().date(), df["date"].max().date()
    if "f_all_years" not in st.session_state:
        _reset(df)

    st.sidebar.header("🔎 Bộ lọc chung")
    st.sidebar.button("↺ Đặt lại bộ lọc", on_click=_reset, args=(df,), use_container_width=True)

    st.sidebar.subheader("Thời gian")
    all_years = st.sidebar.checkbox("Chọn tất cả các năm", key="f_all_years")
    if all_years:
        st.session_state["f_years"] = years
    sel_years = st.sidebar.multiselect("Năm", years, key="f_years", disabled=all_years)
    sel_months = st.sidebar.multiselect("Tháng", MONTHS, key="f_months")
    sel_quarters = st.sidebar.multiselect("Quý", QUARTERS, key="f_quarters")
    dates = st.sidebar.date_input("Khoảng ngày", min_value=dmin, max_value=dmax, key="f_dates")

    st.sidebar.subheader("Thuộc tính khác")
    sel = {}
    for key, col, label in _MULTI:
        sel[col] = st.sidebar.multiselect(label, sorted(df[col].unique()), key=key)

    # date_input có thể trả về 1 phần tử khi người dùng đang chọn dở
    if isinstance(dates, (tuple, list)) and len(dates) == 2:
        d1, d2 = dates
    else:
        d1 = d2 = dates[0] if isinstance(dates, (tuple, list)) and dates else dmin

    # Các bộ lọc áp dụng đồng thời (giao nhau) nên luôn đồng bộ với nhau
    mask = (df["year"].isin(sel_years) & df["month"].isin(sel_months) & df["quarter"].isin(sel_quarters)
            & (df["date"] >= pd.Timestamp(d1)) & (df["date"] <= pd.Timestamp(d2)))
    for col, vals in sel.items():
        mask &= df[col].isin(vals)
    out = df[mask]
    st.sidebar.caption(f"Đang hiển thị {len(out):,} / {len(df):,} đơn hàng")
    return out
