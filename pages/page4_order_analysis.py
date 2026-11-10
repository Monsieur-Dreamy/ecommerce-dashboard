"""PAGE 4 - Giá trị và cơ cấu đơn hàng."""
import pandas as pd
import streamlit as st
from utils import calculations as calc, charts as ch


def render(df: pd.DataFrame):
    st.title("🧾 Phân tích giá trị và cơ cấu đơn hàng")
    st.caption("Phân tích giá trị đơn, số lượng sản phẩm, số dòng sản phẩm. Bộ lọc thời gian/quốc gia lấy từ Sidebar.")
    s = calc.sales(df)
    if ch.empty_guard(df):
        return

    n = st.slider("Top N đơn hàng có net_revenue cao nhất", 5, 50, 10, key="p4_topn")
    top = s.nlargest(n, "net_revenue")[["order_id", "net_revenue", "units", "line_count", "country_code", "customer_segment", "year"]]
    a, b = st.columns(2)
    with a:
        st.subheader(f"Top {n} đơn hàng")
        st.caption("Các đơn có doanh thu thuần cao nhất.")
        ch.show(ch.bar(top, "order_id", "net_revenue", f"Top {n} đơn hàng theo net_revenue", "Mã đơn", "Doanh thu thuần", horizontal=True))
    with b:
        st.subheader("Phân phối giá trị đơn")
        st.caption("Histogram: đa số đơn tập trung ở mức giá trị nào.")
        ch.show(ch.histogram_stats(s, "net_revenue", "Phân phối giá trị đơn hàng (net_revenue)", "Doanh thu thuần/đơn"))

    st.subheader("Boxplot giá trị đơn theo phân khúc")
    st.caption("So sánh trung vị, độ phân tán và ngoại lệ của net_revenue giữa các phân khúc.")
    ch.show(ch.box(s, "customer_segment", "net_revenue", "Phân phối net_revenue theo phân khúc", "Phân khúc", "Doanh thu thuần/đơn"))

    ys = s.groupby("year").agg(aov=("net_revenue", "mean"), units_avg=("units", "mean"), lines_avg=("line_count", "mean")).reset_index()
    c = st.columns(3)
    with c[0]:
        ch.show(ch.bar(ys, "year", "aov", "Giá trị đơn TB theo năm", "Năm", "Giá trị đơn TB", color="year"))
    with c[1]:
        ch.show(ch.bar(ys, "year", "units_avg", "Số SP TB mỗi đơn", "Năm", "Số SP TB", color="year"))
    with c[2]:
        ch.show(ch.bar(ys, "year", "lines_avg", "Số dòng SP TB mỗi đơn", "Năm", "Số dòng TB", color="year"))

    a, b = st.columns(2)
    with a:
        st.subheader("Phân bố số dòng sản phẩm")
        lc = s.groupby(["year", "line_count"]).size().reset_index(name="orders")
        ch.show(ch.bar(lc, "line_count", "orders", "Số đơn theo số dòng sản phẩm", "Số dòng SP", "Số đơn", color="year", text=False))
    with b:
        st.subheader("Số lượng SP và giá trị đơn")
        st.caption("Mỗi điểm là một đơn (mẫu tối đa 5.000 đơn).")
        ch.show(ch.scatter(s.sample(min(5000, len(s)), random_state=1), "units", "net_revenue", "Số lượng SP vs giá trị đơn", "Số lượng SP", "Doanh thu thuần"))

    st.subheader("Pivot Table: doanh thu theo quốc gia × phân khúc khách hàng")
    pv = pd.pivot_table(s, index="country_code", columns="customer_segment", values="net_revenue", aggfunc="sum", margins=True, margins_name="Tổng")
    st.dataframe(pv.style.format("{:,.0f}"), use_container_width=True)
    with st.expander("So sánh Pivot Table giữa các năm"):
        for y in sorted(s["year"].unique()):
            st.markdown(f"**Năm {y}**")
            st.dataframe(pd.pivot_table(s[s["year"] == y], index="country_code", columns="customer_segment", values="net_revenue",
                                        aggfunc="sum", margins=True, margins_name="Tổng").style.format("{:,.0f}"), use_container_width=True)
    ch.table(top, "top_don_hang", "Bảng Top N đơn hàng", {"net_revenue": "{:,.2f}"})

    st.subheader("💡 Nhận xét")
    corr = s["units"].corr(s["net_revenue"])
    st.write(f"- Đơn cao nhất: **{top.iloc[0]['order_id']}** ({top.iloc[0]['net_revenue']:,.2f}). Giá trị đơn TB: **{s['net_revenue'].mean():,.2f}**, trung vị: {s['net_revenue'].median():,.2f}"
             f"{' (TB > trung vị: phân phối lệch phải, có một số đơn giá trị lớn)' if s['net_revenue'].mean() > s['net_revenue'].median() else ''}.")
    st.write(f"- Tương quan giữa số lượng SP và giá trị đơn: **{corr:.2f}**. Trung bình {s['units'].mean():.2f} SP và {s['line_count'].mean():.2f} dòng/đơn.")
    seg = s.groupby("customer_segment")["net_revenue"].sum().sort_values(ascending=False)
    ctr = s.groupby("country_code")["net_revenue"].sum().sort_values(ascending=False)
    st.write(f"- Phân khúc đóng góp nhiều nhất: **{seg.index[0]}** ({seg.iloc[0]/seg.sum()*100:.1f}%); quốc gia nhiều nhất: **{ctr.index[0]}** ({ctr.iloc[0]/ctr.sum()*100:.1f}%).")
