"""Các hàm tính KPI, doanh thu, tăng trưởng, tỷ trọng.
Quy tắc chung: doanh thu/đơn bán thành công chỉ tính các dòng is_sale == True."""
import pandas as pd


def sales(df: pd.DataFrame) -> pd.DataFrame:
    """Đơn bán thành công: net_revenue > 0 và status không phải cancelled/refunded."""
    return df[df["is_sale"]]


def kpis(df: pd.DataFrame) -> dict:
    s = sales(df)
    n_orders = s["order_id"].nunique()
    revenue = s["net_revenue"].sum()
    return {
        "revenue": revenue,
        "orders": n_orders,
        "units": int(s["units"].sum()),
        "customers": s["customer_id"].nunique(),
        "total_orders": df["order_id"].nunique(),  # mọi trạng thái
        "aov": revenue / n_orders if n_orders else 0,
    }


def growth(new, old):
    """Tốc độ tăng trưởng (%); None nếu không có kỳ gốc."""
    if old is None or old == 0 or pd.isna(old):
        return None
    return (new - old) / old * 100


def fmt_growth(g) -> str:
    return "N/A" if g is None or pd.isna(g) else f"{g:+.1f}%"


def summary_by(df: pd.DataFrame, cols) -> pd.DataFrame:
    """Doanh thu, số đơn, số lượng, số khách hàng, tỷ trọng theo nhóm cols."""
    cols = [cols] if isinstance(cols, str) else list(cols)
    s = sales(df)
    if s.empty:
        return pd.DataFrame(columns=cols + ["revenue", "orders", "units", "customers", "share"])
    g = s.groupby(cols).agg(revenue=("net_revenue", "sum"), orders=("order_id", "nunique"),
                            units=("units", "sum"), customers=("customer_id", "nunique")).reset_index()
    # Nếu có cột year cùng cột khác: tỷ trọng tính trong từng năm
    if "year" in cols and len(cols) > 1 and cols[0] == "year":
        g["share"] = g["revenue"] / g.groupby("year")["revenue"].transform("sum") * 100
    else:
        g["share"] = g["revenue"] / g["revenue"].sum() * 100
    return g


def yearly_table(df: pd.DataFrame) -> pd.DataFrame:
    """Bảng theo năm + tăng trưởng so với năm trước."""
    t = summary_by(df, "year").sort_values("year").reset_index(drop=True)
    t["aov"] = t["revenue"] / t["orders"]
    t["revenue_growth"] = t["revenue"].pct_change() * 100
    t["orders_growth"] = t["orders"].pct_change() * 100
    return t


def time_series(df: pd.DataFrame, level: str) -> pd.DataFrame:
    """level: Ngày/Tháng/Quý/Năm -> bảng doanh thu theo kỳ."""
    s = sales(df).copy()
    if s.empty:
        return pd.DataFrame(columns=["period", "revenue", "orders", "growth"])
    if level == "Ngày":
        s["period"] = s["date"]
    elif level == "Tháng":
        s["period"] = s["ordered_at"].dt.to_period("M").dt.to_timestamp()
    elif level == "Quý":
        s["period"] = s["year"].astype(str) + "-Q" + s["quarter"].astype(str)
    else:
        s["period"] = s["year"].astype(str)
    t = s.groupby("period").agg(revenue=("net_revenue", "sum"), orders=("order_id", "nunique")).reset_index()
    t = t.sort_values("period").reset_index(drop=True)
    t["growth"] = t["revenue"].pct_change() * 100
    return t


def monthly_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """Doanh thu theo (year, month) - mỗi năm một đường."""
    return summary_by(df, ["year", "month"]).sort_values(["year", "month"])
