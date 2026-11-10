"""PAGE 5 - Khách hàng và kênh tiếp cận."""
import pandas as pd
import streamlit as st
from utils import calculations as calc, charts as ch


def render(df: pd.DataFrame):
    st.title("🎯 Phân tích khách hàng và kênh tiếp cận")
    st.caption("Hiệu quả của các kênh tiếp cận và phân khúc khách hàng. Bộ lọc thời gian/quốc gia/năm lấy từ Sidebar.")
    if ch.empty_guard(df):
        return
    chn = calc.summary_by(df, "acquisition_channel").sort_values("revenue", ascending=False)
    seg = calc.summary_by(df, "customer_segment").sort_values("revenue", ascending=False)

    st.subheader("Kênh tiếp cận")
    a, b = st.columns(2)
    with a:
        ch.show(ch.bar(chn, "acquisition_channel", "revenue", "Doanh thu theo kênh", "Kênh", "Doanh thu thuần"))
    with b:
        ch.show(ch.pie(chn, "acquisition_channel", "revenue", "Tỷ trọng doanh thu theo kênh"))
    cy = calc.summary_by(df, ["year", "acquisition_channel"])
    ch.show(ch.bar(cy, "acquisition_channel", "revenue", "Doanh thu theo kênh qua các năm", "Kênh", "Doanh thu thuần", color="year", text=False))

    st.caption("Stacked bar: cơ cấu doanh thu theo kênh trong từng năm.")
    ch.show(ch.bar(cy.assign(year=cy["year"].astype(str)), "year", "revenue", "Cơ cấu doanh thu theo kênh (stacked)", "Năm",
                   "Doanh thu thuần", color="acquisition_channel", barmode="stack", text=False))

    st.subheader("Phân khúc khách hàng")
    a, b = st.columns(2)
    with a:
        ch.show(ch.bar(seg, "customer_segment", "revenue", "Doanh thu theo phân khúc", "Phân khúc", "Doanh thu thuần"))
    with b:
        cust = df[df["is_sale"]].groupby("customer_segment")["customer_id"].nunique().reset_index(name="customers")
        ch.show(ch.pie(cust, "customer_segment", "customers", "Cơ cấu khách hàng theo phân khúc"))
    sy = calc.summary_by(df, ["year", "customer_segment"])
    ch.show(ch.bar(sy, "customer_segment", "revenue", "Doanh thu theo phân khúc qua các năm", "Phân khúc", "Doanh thu thuần", color="year", text=False))

    st.subheader("Số khách hàng qua các năm")
    st.caption("Khách hàng duy nhất (customer_id) có đơn bán thành công trong từng năm.")
    yc = calc.summary_by(df, "year")
    ch.show(ch.bar(yc, "year", "customers", "Số khách hàng theo năm", "Năm", "Số khách hàng", color="year"))

    f = {"revenue": "{:,.0f}", "share": "{:.1f}"}
    ren = {"revenue": "Doanh thu", "orders": "Số đơn", "customers": "Số KH", "share": "Tỷ trọng (%)", "units": "Số lượng SP"}
    ch.table(chn.rename(columns={**ren, "acquisition_channel": "Kênh"}), "kenh", "Bảng thống kê theo kênh", {"Doanh thu": "{:,.0f}", "Tỷ trọng (%)": "{:.1f}"})
    ch.table(seg.rename(columns={**ren, "customer_segment": "Phân khúc"}), "phan_khuc", "Bảng thống kê theo phân khúc", {"Doanh thu": "{:,.0f}", "Tỷ trọng (%)": "{:.1f}"})

    st.subheader("💡 Nhận xét")
    st.write(f"- Kênh doanh thu cao nhất: **{chn.iloc[0]['acquisition_channel']}** ({chn.iloc[0]['share']:.1f}%). Phân khúc đóng góp lớn nhất: **{seg.iloc[0]['customer_segment']}** ({seg.iloc[0]['share']:.1f}%).")
    yrs = sorted(cy["year"].unique())
    if len(yrs) >= 2:
        y0, y1 = yrs[0], yrs[-1]
        for name, data, col in [("Kênh", cy, "acquisition_channel"), ("Phân khúc", sy, "customer_segment")]:
            p = data.pivot(index=col, columns="year", values="revenue")
            gr = ((p[y1] - p[y0]) / p[y0] * 100).dropna().sort_values(ascending=False)
            sh = data.pivot(index=col, columns="year", values="share")
            dsh = (sh[y1] - sh[y0]).dropna()
            st.write(f"- {name} tăng trưởng nhanh nhất {int(y0)}→{int(y1)}: **{gr.index[0]}** ({gr.iloc[0]:+.1f}%); chậm nhất: **{gr.index[-1]}** ({gr.iloc[-1]:+.1f}%). "
                     f"Cơ cấu thay đổi nhiều nhất: **{dsh.abs().idxmax()}** ({dsh[dsh.abs().idxmax()]:+.2f} điểm %).")
    else:
        st.write("- Chọn từ 2 năm trở lên để so sánh xu hướng các kênh/phân khúc.")
