"""PAGE 3 - Phân tích doanh thu theo quốc gia."""
import pandas as pd
import streamlit as st
from utils import calculations as calc, charts as ch


def render(df: pd.DataFrame):
    st.title("🌍 Phân tích doanh thu theo quốc gia")
    st.caption("So sánh doanh thu, đơn hàng và tỷ trọng giữa các quốc gia (chỉ theo country_code).")
    if ch.empty_guard(df):
        return
    opts = sorted(df["country_code"].unique())
    sel = st.multiselect("Chọn quốc gia", opts, default=opts, key="p3_countries")
    d = df[df["country_code"].isin(sel)]
    if ch.empty_guard(d):
        return

    cs = calc.summary_by(d, "country_code").sort_values("revenue", ascending=False)
    a, b = st.columns(2)
    with a:
        st.subheader("Doanh thu theo quốc gia")
        st.caption("Tổng doanh thu thuần của từng quốc gia trong bộ lọc.")
        ch.show(ch.bar_labeled(cs, "country_code", "revenue", [f"{v:.1f}%" for v in cs["share"]],
                               "Doanh thu thuần theo quốc gia (nhãn: tỷ trọng)", "Quốc gia", "Doanh thu thuần"))
    with b:
        st.subheader("Tỷ trọng doanh thu")
        st.caption("Phần đóng góp của mỗi quốc gia vào tổng doanh thu.")
        ch.show(ch.pie(cs, "country_code", "revenue", "Tỷ trọng doanh thu theo quốc gia"))

    st.subheader("Doanh thu từng quốc gia qua các năm")
    st.caption("Grouped bar: mỗi quốc gia có một cột cho từng năm.")
    cy = calc.summary_by(d, ["year", "country_code"])
    ch.show(ch.bar(cy, "country_code", "revenue", "Doanh thu theo quốc gia và năm", "Quốc gia", "Doanh thu thuần", color="year", text=False))

    t = cs.rename(columns={"country_code": "Quốc gia", "revenue": "Doanh thu", "orders": "Số đơn hàng",
                           "units": "Số lượng SP", "share": "Tỷ trọng DT (%)"})[["Quốc gia", "Doanh thu", "Số đơn hàng", "Số lượng SP", "Tỷ trọng DT (%)"]]
    st.subheader("Bảng thống kê")
    st.dataframe(t.style.format({"Doanh thu": "{:,.0f}", "Tỷ trọng DT (%)": "{:.1f}"}), hide_index=True, use_container_width=True)
    ch.table(cy.rename(columns={"year": "Năm", "country_code": "Quốc gia", "share": "Tỷ trọng trong năm (%)"}), "quocgia_theo_nam",
             "Chi tiết theo quốc gia & năm", {"revenue": "{:,.0f}", "Tỷ trọng trong năm (%)": "{:.1f}"})

    st.subheader("💡 Nhận xét")
    hi, lo = cs.iloc[0], cs.iloc[-1]
    st.write(f"- Cao nhất: **{hi['country_code']}** ({hi['revenue']:,.0f}, {hi['share']:.1f}%); thấp nhất: **{lo['country_code']}** ({lo['revenue']:,.0f}, {lo['share']:.1f}%).")
    yrs = sorted(cy["year"].unique())
    if len(yrs) >= 2:
        y0, y1 = yrs[0], yrs[-1]
        p = cy.pivot(index="country_code", columns="year", values="revenue")
        gr = ((p[y1] - p[y0]) / p[y0] * 100).dropna().sort_values(ascending=False)
        sh = cy.pivot(index="country_code", columns="year", values="share")
        dsh = (sh[y1] - sh[y0]).dropna().sort_values(ascending=False)
        gdf = pd.DataFrame({f"Tăng trưởng DT {int(y0)}→{int(y1)} (%)": gr, f"Thay đổi tỷ trọng (điểm %)": dsh}).reset_index()
        st.write(f"- Tăng trưởng cao nhất {int(y0)}→{int(y1)}: **{gr.index[0]}** ({gr.iloc[0]:+.1f}%). Tỷ trọng tăng nhiều nhất: **{dsh.index[0]}** ({dsh.iloc[0]:+.2f} điểm %).")
        st.dataframe(gdf.style.format({gdf.columns[1]: "{:+.1f}", gdf.columns[2]: "{:+.2f}"}), hide_index=True, use_container_width=True)
    else:
        st.write("- Chọn từ 2 năm trở lên để xem tăng trưởng và thay đổi tỷ trọng.")
