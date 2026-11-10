"""PAGE 2 - Xu hướng doanh thu theo thời gian."""
import pandas as pd
import streamlit as st
from utils import calculations as calc, charts as ch


def render(df: pd.DataFrame):
    st.title("📈 Xu hướng doanh thu theo thời gian")
    st.caption("Theo dõi biến động doanh thu theo ngày/tháng/quý/năm và so sánh từng tháng giữa các năm.")
    if ch.empty_guard(df):
        return

    c1, c2 = st.columns([1, 2])
    level = c1.selectbox("Cấp độ thời gian", ["Ngày", "Tháng", "Quý", "Năm"], index=1)
    dmin, dmax = df["date"].min().date(), df["date"].max().date()
    rng = c2.date_input("Khoảng thời gian (trong dữ liệu đã lọc)", (dmin, dmax), min_value=dmin, max_value=dmax, key="p2_dates")
    if isinstance(rng, (tuple, list)) and len(rng) == 2:
        d = df[(df["date"] >= pd.Timestamp(rng[0])) & (df["date"] <= pd.Timestamp(rng[1]))]
    else:
        d = df
    if ch.empty_guard(d):
        return

    ts = calc.time_series(d, level)
    st.subheader(f"Doanh thu theo {level.lower()}")
    st.caption("Đường doanh thu thuần theo cấp độ thời gian đã chọn.")
    show_ma = st.checkbox("Hiển thị đường trung bình trượt", value=True, key="p2_ma")
    window = 7 if level == "Ngày" else 3
    ttl = f"Xu hướng doanh thu thuần theo {level.lower()}"
    if show_ma:
        ch.show(ch.line_with_ma(ts, "period", "revenue", ttl, level, "Doanh thu thuần", window))
    else:
        ch.show(ch.line(ts, "period", "revenue", ttl, level, "Doanh thu thuần"))

    st.subheader("So sánh doanh thu theo tháng giữa các năm")
    st.caption("Mỗi năm một đường riêng, trục ngang là tháng 1–12.")
    m = calc.monthly_by_year(d)
    fig = ch.line_by_year(m, "month", "revenue", "Doanh thu thuần theo tháng", "Tháng", "Doanh thu thuần")
    fig.update_xaxes(tickmode="linear", dtick=1, range=[0.8, 12.2])
    ch.show(fig)

    a, b = st.columns(2)
    with a:
        st.subheader("Tăng trưởng theo năm")
        yt = calc.yearly_table(d)
        ch.show(ch.bar(yt.dropna(subset=["revenue_growth"]), "year", "revenue_growth", "Tăng trưởng doanh thu so với năm trước (%)",
                       "Năm", "%", color="year")) if len(yt) > 1 else st.info("Cần ≥ 2 năm để tính tăng trưởng.")
    with b:
        st.subheader("Doanh thu theo quý")
        q = calc.summary_by(d, ["year", "quarter"])
        q["quarter"] = "Q" + q["quarter"].astype(str)
        ch.show(ch.bar(q, "quarter", "revenue", "Doanh thu theo quý (mỗi năm một màu)", "Quý", "Doanh thu thuần", color="year", text=False))

    ch.table(ts.rename(columns={"period": "Kỳ", "revenue": "Doanh thu", "orders": "Số đơn", "growth": "Tăng trưởng vs kỳ trước (%)"}),
             "xu_huong", f"Bảng doanh thu theo {level.lower()}", {"Doanh thu": "{:,.0f}", "Tăng trưởng vs kỳ trước (%)": "{:+.1f}"})

    st.subheader("💡 Nhận xét")
    mm = calc.time_series(d, "Tháng")
    top, low = mm.loc[mm["revenue"].idxmax()], mm.loc[mm["revenue"].idxmin()]
    st.write(f"- Tháng doanh thu **cao nhất**: {top['period']:%m/%Y} ({top['revenue']:,.0f}); **thấp nhất**: {low['period']:%m/%Y} ({low['revenue']:,.0f}).")
    g = mm.dropna(subset=["growth"])
    if not g.empty:
        up, dn = g.loc[g["growth"].idxmax()], g.loc[g["growth"].idxmin()]
        st.write(f"- Tăng mạnh nhất: {up['period']:%m/%Y} ({up['growth']:+.1f}% so với tháng trước); giảm mạnh nhất: {dn['period']:%m/%Y} ({dn['growth']:+.1f}%).")
        first, last = mm["revenue"].iloc[: max(1, len(mm)//3)].mean(), mm["revenue"].iloc[-max(1, len(mm)//3):].mean()
        gg = calc.growth(last, first)
        st.write(f"- Xu hướng chung: doanh thu tháng TB ở giai đoạn cuối **{'cao hơn' if gg >= 0 else 'thấp hơn'} {abs(gg):.1f}%** so với giai đoạn đầu." if gg is not None else "")
