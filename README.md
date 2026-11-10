# E-commerce Dashboard (Streamlit + Plotly)

## Cài đặt & chạy
```bash
python -m venv venv
venv\Scripts\activate        # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```
Đặt file `ecommerce-sales-v1.0.0-analysis.xlsx` cùng thư mục với `app.py`.

## Hướng dẫn sử dụng nhanh
Trong Dashboard, mở trang **📖 Hướng dẫn sử dụng** (menu bên trái) để xem cách dùng bộ lọc, ý nghĩa từng trang, cách tính số liệu và phần hỏi đáp.
1. Chọn trang ở menu bên trái.
2. Chọn bộ lọc ở Sidebar (năm, tháng, quý, ngày, quốc gia, trạng thái, kênh, phân khúc); bấm "Đặt lại bộ lọc" để về mặc định.
3. KPI, biểu đồ và bảng tự cập nhật; mở mục 📋 để xem bảng và tải CSV.

## Chạy EDA và tạo ảnh cho báo cáo
```bash
python eda_report.py
```
In các bảng EDA (thiếu/trùng, thống kê mô tả, ngoại lệ, groupby, pivot), lưu 9 biểu đồ vào `assets/` và bảng tổng hợp vào `data/eda_tables.json`. Các ảnh trong báo cáo Word chính là các file trong `assets/`.

## Cách tích hợp 5 sinh viên
- Mỗi người chỉ sửa 1 file trong `pages/`, viết hàm `render(df)` nhận DataFrame ĐÃ LỌC (không đọc Excel, không tạo bộ lọc riêng).
- Dùng `utils.calculations` (summary_by, kpis, yearly_table...) và `utils.charts` để thống nhất quy tắc.
- `app.py` đã đăng ký sẵn 5 page qua `st.navigation`, nên thư mục `pages/` không bị Streamlit tự tạo menu trùng.

## Quy tắc dữ liệu
- Đơn bán thành công: `net_revenue > 0` và status không phải `cancelled`/`refunded` (cột `is_sale`).
- Doanh thu = tổng `net_revenue` của đơn bán thành công; đếm đơn/khách bằng `nunique`.
- Không giả định đơn vị tiền tệ.

## Lỗi thường gặp
- `FileNotFoundError`: sai tên/vị trí file Excel.
- `ModuleNotFoundError: utils`: chạy `streamlit run app.py` từ thư mục gốc dự án.
- `st.navigation` không tồn tại: nâng cấp `pip install -U streamlit` (cần >= 1.36).
- Trang trống: bộ lọc quá hẹp, bấm "Đặt lại bộ lọc".
