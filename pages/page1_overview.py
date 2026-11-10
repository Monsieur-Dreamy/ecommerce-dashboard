"""PAGE 1 - Tổng quan kinh doanh."""
import pandas as pd
import streamlit as st
from utils import calculations as calc, charts as ch


def render(df: pd.DataFrame):
    st.title("📊 Tổng quan kinh doanh")
    st.caption("Bức tranh chung về doanh thu, đơn hàng, sản phẩm và khách hàng. "
               "Doanh thu = tổng net_revenue của đơn bán thành công (net_revenue > 0, không cancelled/refunded).")
    if ch.empty_guard(df):
        return

    yt = calc.yearly_table(df)
    k = calc.kpis(df)
    # So sánh kỳ hiện tại (năm mới nhất) với kỳ trước (năm liền trước) nếu có
    d = {}
    if len(yt) >= 2:
        cur, prev = yt.iloc[-1]["year"], yt.iloc[-2]["year"]
        kc, kp = calc.kpis(df[df["year"] == cur]), calc.kpis(df[df["year"] == prev])
        d = {m: calc.fmt_growth(calc.growth(kc[m], kp[m])) for m in ["revenue", "orders", "units", "customers"]}
        st.caption(f"Mũi tên so sánh: {int(cur)} so với {int(prev)}.")
    c = st.columns(4)
    c[0].metric("Tổng doanh thu thuần", f"{k['revenue']:,.0f}", d.get("revenue"))
    c[1].metric("Đơn hàng bán thành công", f"{k['orders']:,}", d.get("orders"))
    c[2].metric("Tổng số lượng sản phẩm", f"{k['units']:,}", d.get("units"))
    c[3].metric("Số khách hàng", f"{k['customers']:,}", d.get("customers"))

    st.divider()
    a, b = st.columns(2)
    with a:
        st.subheader("Doanh thu theo trạng thái đơn hàng")
        st.caption("Net_revenue (>0) và số đơn của từng trạng thái; cancelled/refunded không tạo doanh thu bán hàng.")
        st_df = df.assign(rev=df["net_revenue"].where(df["net_revenue"] > 0, 0)).groupby("order_status").agg(
            revenue=("rev", "sum"), orders=("order_id", "nunique")).reset_index()
        ch.show(ch.bar(st_df, "order_status", "revenue", "Doanh thu theo trạng thái", "Trạng thái", "Doanh thu thuần"))
    with b:
        st.subheader("So sánh doanh thu giữa các năm")
        st.caption("Mỗi cột là một năm, không cộng gộp.")
        ch.show(ch.bar(yt, "year", "revenue", "Doanh thu thuần theo năm", "Năm", "Doanh thu thuần", color="year"))

    st.subheader("Số đơn hàng theo trạng thái")
    st.caption("Đếm số đơn (order_id duy nhất) của từng trạng thái, kèm tỷ lệ %. Đơn cancelled và refunded có "
               "net_revenue = 0 nên không xuất hiện ở biểu đồ doanh thu phía trên, nhưng vẫn là đơn hàng.")
    cnt = df.groupby("order_status")["order_id"].nunique().reset_index(name="orders").sort_values("orders", ascending=False)
    labels = [f"{o:,} ({o / cnt['orders'].sum() * 100:.1f}%)" for o in cnt["orders"]]
    ch.show(ch.bar_labeled(cnt, "order_status", "orders", labels, "Số đơn hàng theo trạng thái", "Trạng thái", "Số đơn hàng"))

    with st.expander("📋 Bảng thống kê theo năm", expanded=True):
        t = yt.rename(columns={"year": "Năm", "revenue": "Doanh thu", "orders": "Số đơn", "units": "Số lượng SP",
                               "customers": "Số KH", "aov": "Giá trị đơn TB", "revenue_growth": "Tăng trưởng DT (%)",
                               "orders_growth": "Tăng trưởng đơn (%)"}).drop(columns="share")
        st.dataframe(t.style.format({"Doanh thu": "{:,.0f}", "Giá trị đơn TB": "{:,.2f}", "Tăng trưởng DT (%)": "{:+.1f}",
                                     "Tăng trưởng đơn (%)": "{:+.1f}"}, na_rep="N/A"), hide_index=True, use_container_width=True)
    ov = pd.DataFrame({"Chỉ số": ["Tổng số đơn (mọi trạng thái)", "Đơn bán thành công", "Tổng doanh thu thuần",
                                  "Giá trị đơn trung bình", "Tổng số lượng SP", "Số khách hàng"],
                       "Giá trị": [f"{k['total_orders']:,}", f"{k['orders']:,}", f"{k['revenue']:,.0f}",
                                   f"{k['aov']:,.2f}", f"{k['units']:,}", f"{k['customers']:,}"]})
    ch.table(ov, "tong_quan_chi_so", "Bảng tổng quan các chỉ số")

    st.subheader("💡 Nhận xét")
    hi, lo = yt.loc[yt["revenue"].idxmax()], yt.loc[yt["revenue"].idxmin()]
    st.write(f"- Năm doanh thu **cao nhất**: **{int(hi['year'])}** ({hi['revenue']:,.0f}); **thấp nhất**: **{int(lo['year'])}** ({lo['revenue']:,.0f}).")
    for _, r in yt.dropna(subset=["revenue_growth"]).iterrows():
        st.write(f"- {int(r['year'])}: doanh thu {'tăng' if r['revenue_growth'] >= 0 else 'giảm'} **{abs(r['revenue_growth']):.1f}%** so với năm trước.")
    if len(yt) == 1:
        st.write("- Chọn từ 2 năm trở lên để xem tốc độ tăng trưởng.")
