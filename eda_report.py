"""EDA + trực quan hóa cho báo cáo (Phần 2 và Phần 3).

Chạy:  python eda_report.py
Kết quả:
  - In ra màn hình các bảng EDA (thiếu/trùng, thống kê mô tả, ngoại lệ, trạng thái, groupby, pivot).
  - Lưu 9 biểu đồ vào assets/  (các ảnh này được chèn vào báo cáo Word).
  - Lưu các bảng tổng hợp vào data/eda_tables.json.
Dùng chung utils/ với Dashboard nên số liệu trùng khớp với Dashboard.
"""
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

from utils.load_data import load_raw_data
from utils.clean_data import clean_data, quality_report
from utils import calculations as c

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS, DATA = os.path.join(BASE, "assets"), os.path.join(BASE, "data")
os.makedirs(ASSETS, exist_ok=True)
os.makedirs(DATA, exist_ok=True)
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)

YEAR_COLORS = {2023: "#4C78A8", 2024: "#F58518", 2025: "#54A24B"}
MILLION = FuncFormatter(lambda v, _: f"{v/1e6:.2f}M")
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": .3, "axes.axisbelow": True})


def title(text):
    print("\n" + "=" * 8, text, "=" * 8)


def new_fig():
    return plt.subplots(figsize=(7, 3.5))


def save(name):
    plt.tight_layout()
    plt.savefig(os.path.join(ASSETS, name), dpi=170)
    plt.close()
    print("  đã lưu assets/" + name)


# ---------------------------------------------------------------- Đọc & làm sạch dữ liệu (dùng chung utils/)
raw = load_raw_data()
df = clean_data(raw)
s = c.sales(df)

# ---------------------------------------------------------------- Phần 1: Mô tả dữ liệu
title("Phần 1. Mô tả dữ liệu")
print(f"  File: {os.path.basename(os.path.join(BASE, 'ecommerce-sales-v1.0.0-analysis.xlsx'))}  |  Sheet: Ecommerce Sales & Returns Datas")
print(f"  Số dòng x số cột: {raw.shape[0]:,} x {raw.shape[1]}")
raw_dt = pd.to_datetime(raw["ordered_at"], utc=True)
print(f"  Thời gian đặt hàng: {raw_dt.min()} -> {raw_dt.max()}")
info = pd.DataFrame({"dtype_goc": raw.dtypes.astype(str), "dtype_sau_xu_ly": df[raw.columns].dtypes.astype(str),
                     "so_gia_tri_duy_nhat": raw.nunique(), "vi_du_dong_dau": raw.iloc[0].astype(str)})
print(info.to_string())
for col in ["order_status", "country_code", "acquisition_channel", "customer_segment"]:
    print(f"  {col}: {sorted(raw[col].unique())}")
# Kiểm tra quan hệ giữa các cột tiền
print("  gross_payment = subtotal + tax_amount + shipping_amount (trừ đơn cancelled):",
      f"{((raw.subtotal + raw.tax_amount + raw.shipping_amount - raw.gross_payment).abs() < 0.015)[raw.order_status != 'cancelled'].mean()*100:.2f}% dòng khớp")
print("  net_revenue = gross_payment - refund_amount:",
      f"{((raw.gross_payment - raw.refund_amount - raw.net_revenue).abs() < 0.015).mean()*100:.2f}% dòng khớp")

# ---------------------------------------------------------------- 2.1 Kiểm tra dữ liệu

title("2.1 Kiểm tra dữ liệu")
print(raw.dtypes.to_string())
for k, v in quality_report(raw).items():
    print(f"  {k}: {v}")
print("  net_revenue = 0 theo trạng thái:", df[df.net_revenue == 0].order_status.value_counts().to_dict())

# ---------------------------------------------------------------- 2.2 Thống kê mô tả
title("2.2 Thống kê mô tả")
num = ["line_count", "units", "subtotal", "tax_amount", "shipping_amount", "gross_payment", "refund_amount", "net_revenue"]
print(raw[num].describe().T.round(2))
status = df.groupby("order_status").agg(orders=("order_id", "count"), refund=("refund_amount", "sum"))
status["ty_le_%"] = (status.orders / len(df) * 100).round(2)
print(status)
print(f"  Tổng hoàn tiền: {df.refund_amount.sum():,.0f} / gross_payment {df.gross_payment.sum():,.0f} "
      f"= {df.refund_amount.sum()/df.gross_payment.sum()*100:.2f}%")

# ---------------------------------------------------------------- 2.3 Ngoại lệ (IQR)
title("2.3 Ngoại lệ net_revenue (IQR, đơn bán thành công)")
q1, q3 = s.net_revenue.quantile([.25, .75])
upper = q3 + 1.5 * (q3 - q1)
n_out = int((s.net_revenue > upper).sum())
print(f"  Q1={q1:.2f}  Q3={q3:.2f}  IQR={q3-q1:.2f}  ngưỡng trên={upper:.2f}")
print(f"  Số đơn vượt ngưỡng: {n_out:,} ({n_out/len(s)*100:.2f}%)  max={s.net_revenue.max():,.2f}")
print(f"  Trung bình={s.net_revenue.mean():.2f}  trung vị={s.net_revenue.median():.2f}  skew={s.net_revenue.skew():.2f}")
print(f"  Đơn có units >= 10: {(s.units >= 10).sum()}")

# ---------------------------------------------------------------- 2.4 Lọc theo điều kiện
title("2.4 Lọc dữ liệu theo điều kiện")
print("  Đơn bán thành công:", len(s))
print("  US năm 2025:", len(s[(s.country_code == "US") & (s.year == 2025)]))
print("  net_revenue > 1000:", int((s.net_revenue > 1000).sum()))
print("  partially_refunded được tính bán thành công:", int(df[(df.order_status == "partially_refunded") & df.is_sale].shape[0]))

# ---------------------------------------------------------------- 2.5 GroupBy
title("2.5 GroupBy")
yt = c.yearly_table(df)
print(yt.round(2).to_string(index=False))


def fmt_n(v):
    return f"{v:,.0f}".replace(",", ".")


def fmt_d(v):
    return f"{v:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_g(v):
    return ("+" if v > 0 else ("−" if v < 0 else "")) + f"{abs(v):.1f}".replace(".", ",") + "%"


tables = {}
for key, col in [("country", "country_code"), ("channel", "acquisition_channel"), ("segment", "customer_segment")]:
    t = c.summary_by(df, col).sort_values("revenue", ascending=False)
    p = c.summary_by(df, ["year", col]).pivot(index=col, columns="year", values="revenue")
    A, B = [], []
    for _, r in t.iterrows():
        k = r[col]
        A.append([k, fmt_n(p.loc[k, 2023]), fmt_n(p.loc[k, 2024]), fmt_n(p.loc[k, 2025]), fmt_n(r.revenue),
                  f"{r.share:.2f}%".replace(".", ","), fmt_g((p.loc[k, 2025] / p.loc[k, 2023] - 1) * 100)])
        B.append([k, fmt_n(r.orders), fmt_n(r.units), fmt_n(r.customers), fmt_d(r.revenue / r.orders)])
    y, tot, n_ord = p.sum(), s.net_revenue.sum(), s.order_id.nunique()
    A.append(["Tổng", fmt_n(y[2023]), fmt_n(y[2024]), fmt_n(y[2025]), fmt_n(tot), "100,00%", fmt_g((y[2025] / y[2023] - 1) * 100)])
    B.append(["Tổng", fmt_n(n_ord), fmt_n(s.units.sum()), fmt_n(s.customer_id.nunique()), fmt_d(tot / n_ord)])
    tables[key] = {"A": A, "B": B}
    print(f"\n-- Theo {col}")
    print(t.round(2).to_string(index=False))
    print(p.assign(Tong=p.sum(axis=1)).round(0).to_string())
with open(os.path.join(DATA, "eda_tables.json"), "w", encoding="utf-8") as f:
    json.dump(tables, f, ensure_ascii=False)

# ---------------------------------------------------------------- 2.6 Pivot Table
title("2.6 Pivot Table quốc gia x phân khúc")
SEG = ["consumer", "small_business", "enterprise"]


def fmt_p(v):
    return f"{v:.2f}".replace(".", ",") + "%"


rev = pd.pivot_table(s, index="country_code", columns="customer_segment", values="net_revenue", aggfunc="sum")[SEG]
rev = rev.loc[cs_order] if (cs_order := c.summary_by(df, "country_code").sort_values("revenue", ascending=False).country_code.tolist()) else rev
orders_pv = pd.pivot_table(s, index="country_code", columns="customer_segment", values="order_id", aggfunc="nunique")[SEG].loc[cs_order]
aov = pd.pivot_table(s, index="country_code", columns="customer_segment", values="net_revenue", aggfunc="mean")[SEG].loc[cs_order]
aov_all_country = s.groupby("country_code").net_revenue.mean().loc[cs_order]
aov_all_seg = s.groupby("customer_segment").net_revenue.mean()[SEG]
row_share = rev.div(rev.sum(axis=1), axis=0) * 100          # cơ cấu phân khúc trong từng quốc gia
col_share = rev.div(rev.sum(axis=0), axis=1) * 100          # tỷ trọng quốc gia trong từng phân khúc
cell_share = rev / rev.values.sum() * 100                   # tỷ trọng từng ô trên tổng doanh thu

print("Doanh thu (có tổng):")
print(pd.pivot_table(s, index="country_code", columns="customer_segment", values="net_revenue",
                     aggfunc="sum", margins=True, margins_name="Tổng")[SEG + ["Tổng"]].round(0))
print("\nCơ cấu phân khúc trong từng quốc gia (% theo hàng):\n", row_share.round(2))
print("\nTỷ trọng quốc gia trong từng phân khúc (% theo cột):\n", col_share.round(2))
print("\nTỷ trọng từng ô trên tổng doanh thu (%):\n", cell_share.round(2))
print("\nSố đơn:\n", orders_pv)
print("\nGiá trị đơn trung bình:\n", aov.round(1))

# Kiểm định chi-bình phương độc lập: cơ cấu phân khúc có phụ thuộc quốc gia không? (dựa trên số đơn)
o = orders_pv.values.astype(float)
exp = o.sum(1, keepdims=True) * o.sum(0, keepdims=True) / o.sum()
chi2 = float(((o - exp) ** 2 / exp).sum())
dof = (o.shape[0] - 1) * (o.shape[1] - 1)
x = chi2 / 2  # dof chẵn: p = exp(-x) * sum_{k<dof/2} x^k / k!
p_val = float(np.exp(-x) * sum(x ** k / math.factorial(k) for k in range(dof // 2))) if dof % 2 == 0 else float("nan")
cramer_v = float(np.sqrt(chi2 / (o.sum() * (min(o.shape) - 1))))
print(f"\nChi-bình phương = {chi2:.2f}, dof = {dof}, p = {p_val:.4f}, Cramér's V = {cramer_v:.4f}")

fmt_rows = lambda df_, f: [[i] + [f(v) for v in r] for i, r in df_.iterrows()]
total_rev = rev.values.sum()
tables["pivot"] = {
    "revenue": [[i] + [fmt_n(v) for v in r] + [fmt_n(r.sum())] for i, r in rev.iterrows()]
               + [["Tổng"] + [fmt_n(v) for v in rev.sum()] + [fmt_n(total_rev)]],
    "row_share": fmt_rows(row_share, fmt_p),
    "col_share": fmt_rows(col_share, fmt_p),
    "orders": fmt_rows(orders_pv, fmt_n) + [["Tổng"] + [fmt_n(v) for v in orders_pv.sum()] + [fmt_n(orders_pv.values.sum())]],
    "aov": [[i] + [fmt_d(v) for v in r] + [fmt_d(aov_all_country[i])] for i, r in aov.iterrows()]
           + [["Tất cả"] + [fmt_d(v) for v in aov_all_seg] + [fmt_d(s.net_revenue.mean())]],
    "chi2": {"chi2": round(chi2, 2), "dof": dof, "p": round(p_val, 4), "cramer_v": round(cramer_v, 4)},
}
# bảng số đơn: thêm cột Tổng theo từng quốc gia (dòng Tổng đã có sẵn)
for i, r in enumerate(orders_pv.index):
    tables["pivot"]["orders"][i].append(fmt_n(orders_pv.loc[r].sum()))
with open(os.path.join(DATA, "eda_tables.json"), "w", encoding="utf-8") as f:
    json.dump(tables, f, ensure_ascii=False)

# ---------------------------------------------------------------- Phần 3: biểu đồ
title("Phần 3: Biểu đồ (lưu vào assets/)")
# 3.1 Bar doanh thu theo quốc gia
cs = c.summary_by(df, "country_code").sort_values("revenue", ascending=False)
fig, ax = new_fig()
bars = ax.bar(cs.country_code, cs.revenue, color="#4C78A8")
ax.yaxis.set_major_formatter(MILLION)
for r, v in zip(bars, cs.share):
    ax.text(r.get_x() + r.get_width() / 2, r.get_height(), f"{v:.1f}%", ha="center", va="bottom")
ax.set_title("Doanh thu thuần theo quốc gia (nhãn: tỷ trọng)")
ax.set_xlabel("Quốc gia"); ax.set_ylabel("Doanh thu thuần")
save("fig_3_1_country_revenue.png")

# 3.2 Line doanh thu theo tháng, mỗi năm một đường
mo = c.monthly_by_year(df)
fig, ax = new_fig()
for y, g in mo.groupby("year"):
    ax.plot(g.month, g.revenue, marker="o", label=str(y), color=YEAR_COLORS[y])
ax.set_xticks(range(1, 13)); ax.yaxis.set_major_formatter(MILLION); ax.legend()
ax.set_title("Doanh thu thuần theo tháng, so sánh 2023–2025")
ax.set_xlabel("Tháng"); ax.set_ylabel("Doanh thu thuần")
save("fig_3_2_monthly_by_year.png")

# 3.3 Histogram giá trị đơn
fig, ax = new_fig()
ax.hist(s.net_revenue, bins=60, color="#4C78A8")
ax.axvline(s.net_revenue.mean(), color="#E45756", ls="--", label=f"Trung bình {s.net_revenue.mean():,.0f}")
ax.axvline(s.net_revenue.median(), color="#54A24B", ls="--", label=f"Trung vị {s.net_revenue.median():,.0f}")
ax.legend(); ax.set_title("Phân phối giá trị đơn hàng (net_revenue)")
ax.set_xlabel("Doanh thu thuần/đơn"); ax.set_ylabel("Số đơn hàng")
save("fig_3_3_histogram_order_value.png")

# 3.4 Boxplot theo phân khúc
order = ["consumer", "small_business", "enterprise"]
fig, ax = new_fig()
ax.boxplot([s[s.customer_segment == o].net_revenue for o in order], tick_labels=order, patch_artist=True,
           boxprops=dict(facecolor="#9ecae9"), flierprops=dict(markersize=2, alpha=.3))
ax.set_title("Boxplot net_revenue theo phân khúc khách hàng")
ax.set_xlabel("Phân khúc"); ax.set_ylabel("Doanh thu thuần/đơn")
save("fig_3_4_boxplot_segment.png")

# 3.5 Xu hướng 36 tháng
t = c.time_series(df, "Tháng")
fig, ax = new_fig()
ax.plot(t.period, t.revenue, marker="o", ms=3, color="#4C78A8", label="Doanh thu tháng")
ax.plot(t.period, t.revenue.rolling(3).mean(), color="#E45756", label="TB trượt 3 tháng")
ax.yaxis.set_major_formatter(MILLION); ax.legend()
ax.set_title("Xu hướng doanh thu thuần theo tháng (01/2023–12/2025)")
ax.set_xlabel("Tháng"); ax.set_ylabel("Doanh thu thuần")
save("fig_3_5_trend_monthly.png")

# 3.6 Grouped bar quốc gia x năm
p = c.summary_by(df, ["year", "country_code"]).pivot(index="country_code", columns="year", values="revenue").loc[cs.country_code]
fig, ax = new_fig()
w = .27
for i, y in enumerate(p.columns):
    ax.bar(np.arange(len(p)) + (i - 1) * w, p[y], w, label=str(y), color=YEAR_COLORS[y])
ax.set_xticks(range(len(p))); ax.set_xticklabels(p.index); ax.yaxis.set_major_formatter(MILLION); ax.legend()
ax.set_title("Doanh thu theo quốc gia và năm (grouped bar)")
ax.set_xlabel("Quốc gia"); ax.set_ylabel("Doanh thu thuần")
save("fig_3_6_grouped_country_year.png")

# 3.7 Stacked bar kênh x năm
p = c.summary_by(df, ["year", "acquisition_channel"]).pivot(index="year", columns="acquisition_channel", values="revenue")
p = p[["organic", "paid_search", "paid_social", "referral", "affiliate"]]
fig, ax = new_fig()
bottom = np.zeros(len(p))
for col, clr in zip(p.columns, ["#4C78A8", "#F58518", "#54A24B", "#B279A2", "#9D755D"]):
    ax.bar(p.index.astype(str), p[col], bottom=bottom, label=col, color=clr)
    bottom += p[col].values
ax.yaxis.set_major_formatter(MILLION)
ax.legend(fontsize=8, ncol=5, loc="upper center", bbox_to_anchor=(.5, -.28))
ax.set_title("Cơ cấu doanh thu theo kênh tiếp cận (stacked)")
ax.set_xlabel("Năm"); ax.set_ylabel("Doanh thu thuần")
save("fig_3_7_stacked_channel_year.png")

# 3.8 Số đơn theo trạng thái
sc = df.order_status.value_counts()
fig, ax = new_fig()
bars = ax.bar(sc.index, sc.values, color="#4C78A8")
for r, v in zip(bars, sc.values):
    ax.text(r.get_x() + r.get_width() / 2, v, f"{v:,}\n({v/len(df)*100:.1f}%)", ha="center", va="bottom", fontsize=9)
ax.set_ylim(0, sc.max() * 1.18)
ax.set_title("Số đơn hàng theo trạng thái"); ax.set_xlabel("Trạng thái"); ax.set_ylabel("Số đơn hàng")
save("fig_3_8_orders_by_status.png")

# 3.9 Doanh thu theo năm
fig, ax = new_fig()
bars = ax.bar(yt.year.astype(str), yt.revenue, color=[YEAR_COLORS[y] for y in yt.year])
ax.yaxis.set_major_formatter(MILLION)
for r, v in zip(bars, yt.revenue):
    ax.text(r.get_x() + r.get_width() / 2, v, f"{v:,.0f}", ha="center", va="bottom")
ax.set_ylim(0, yt.revenue.max() * 1.1)
ax.set_title("Doanh thu thuần theo năm"); ax.set_xlabel("Năm"); ax.set_ylabel("Doanh thu thuần")
save("fig_3_9_revenue_by_year.png")
print("\nHoàn tất.")
