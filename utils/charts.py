"""Hàm biểu đồ & bảng dùng chung, thống nhất màu sắc."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

YEAR_COLORS = {"2023": "#4C78A8", "2024": "#F58518", "2025": "#54A24B"}
LAYOUT = dict(template="plotly_white", margin=dict(t=60, b=40, l=40, r=20), legend_title_text="")


def _fin(fig, title, x=None, y=None):
    fig.update_layout(title=title, xaxis_title=x, yaxis_title=y, **LAYOUT)
    return fig


def bar(df, x, y, title, xl=None, yl=None, color=None, barmode="group", horizontal=False, text=True):
    d = df.copy()
    if color == "year":
        d["year"] = d["year"].astype(str)
    cmap = YEAR_COLORS if color == "year" else None
    if horizontal:
        fig = px.bar(d, x=y, y=x, color=color, orientation="h", barmode=barmode, color_discrete_map=cmap)
        fig.update_yaxes(autorange="reversed")
    else:
        fig = px.bar(d, x=x, y=y, color=color, barmode=barmode, color_discrete_map=cmap)
    if text:
        fig.update_traces(texttemplate="%{x:,.0f}" if horizontal else "%{y:,.0f}", textposition="outside")
    return _fin(fig, title, yl if horizontal else xl, xl if horizontal else yl)


def line_by_year(df, x, y, title, xl, yl):
    """Mỗi năm một đường riêng (không cộng gộp)."""
    d = df.copy()
    d["year"] = d["year"].astype(str)
    fig = px.line(d, x=x, y=y, color="year", markers=True, color_discrete_map=YEAR_COLORS)
    return _fin(fig, title, xl, yl)


def line(df, x, y, title, xl, yl):
    return _fin(px.line(df, x=x, y=y, markers=len(df) < 80), title, xl, yl)


def bar_labeled(df, x, y, labels, title, xl, yl, color="#4C78A8"):
    """Cột có nhãn tùy ý trên đầu cột (ví dụ tỷ trọng % hoặc 'số đơn (%)')."""
    fig = go.Figure(go.Bar(x=df[x], y=df[y], text=list(labels), textposition="outside",
                           marker_color=color, cliponaxis=False))
    return _fin(fig, title, xl, yl)


def line_with_ma(df, x, y, title, xl, yl, window=3):
    """Đường doanh thu kèm đường trung bình trượt `window` kỳ."""
    d = df.sort_values(x)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d[x], y=d[y], name="Doanh thu", mode="lines+markers" if len(d) < 80 else "lines",
                             line=dict(color="#4C78A8")))
    fig.add_trace(go.Scatter(x=d[x], y=d[y].rolling(window).mean(), name=f"TB trượt {window} kỳ",
                             mode="lines", line=dict(color="#E45756")))
    return _fin(fig, title, xl, yl)


def histogram_stats(df, x, title, xl, yl="Số đơn hàng", nbins=60):
    """Histogram kèm đường trung bình (đỏ) và trung vị (xanh lá)."""
    fig = px.histogram(df, x=x, nbins=nbins)
    fig.update_traces(marker_color="#4C78A8")
    mean, med = df[x].mean(), df[x].median()
    fig.add_vline(x=mean, line_dash="dash", line_color="#E45756",
                  annotation_text=f"Trung bình {mean:,.0f}", annotation_position="top right")
    fig.add_vline(x=med, line_dash="dash", line_color="#54A24B",
                  annotation_text=f"Trung vị {med:,.0f}", annotation_position="top left")
    return _fin(fig, title, xl, yl)


def pie(df, names, values, title):
    fig = px.pie(df, names=names, values=values, hole=0.4)
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(title=title, **LAYOUT)
    return fig


def histogram(df, x, title, xl, yl="Số đơn hàng", nbins=50):
    return _fin(px.histogram(df, x=x, nbins=nbins), title, xl, yl)


def box(df, x, y, title, xl, yl):
    return _fin(px.box(df, x=x, y=y, color=x), title, xl, yl)


def scatter(df, x, y, title, xl, yl):
    return _fin(px.scatter(df, x=x, y=y, opacity=0.4), title, xl, yl)


def show(fig):
    st.plotly_chart(fig, use_container_width=True)


def table(df: pd.DataFrame, name: str, label="Xem bảng chi tiết", fmt=None):
    """Bảng trong expander + nút tải CSV."""
    with st.expander(f"📋 {label}"):
        st.dataframe(df.style.format(fmt) if fmt else df, use_container_width=True, hide_index=True)
        st.download_button("⬇ Tải CSV", df.to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"{name}.csv", mime="text/csv", key=f"dl_{name}")


def empty_guard(df) -> bool:
    if df.empty or not df["is_sale"].any():
        st.warning("Không có đơn hàng bán thành công với bộ lọc hiện tại.")
        return True
    return False
