"""Trang Hướng dẫn sử dụng Dashboard."""
import streamlit as st


def render(df=None):
    st.title("📖 Hướng dẫn sử dụng")
    st.caption("Giới thiệu nhanh cách xem số liệu, dùng bộ lọc và hiểu các chỉ số trong Dashboard.")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🚀 Bắt đầu nhanh", "🔎 Bộ lọc", "📑 Các trang", "📐 Cách tính số liệu", "❓ Hỏi đáp"])

    with tab1:
        st.markdown("""
**Dashboard dùng để làm gì?**
Phân tích dữ liệu thương mại điện tử giai đoạn 2023–2025: doanh thu, đơn hàng, quốc gia, khách hàng và kênh tiếp cận.

**3 bước để bắt đầu**
1. **Chọn trang** ở menu bên trái (Tổng quan, Xu hướng, Quốc gia, Đơn hàng, Khách hàng & kênh).
2. **Chọn bộ lọc** ở Sidebar (năm, tháng, quý, ngày, quốc gia, trạng thái, kênh, phân khúc).
3. **Xem kết quả**: KPI, biểu đồ và bảng tự cập nhật ngay khi bạn đổi bộ lọc.

**Mặc định** hiển thị toàn bộ dữ liệu 2023–2025. Bấm **↺ Đặt lại bộ lọc** để quay về trạng thái này.
        """)
        if df is not None:
            st.info(f"Với bộ lọc hiện tại, Dashboard đang phân tích **{len(df):,}** đơn hàng.")

    with tab2:
        st.markdown("""
Bộ lọc nằm ở Sidebar và **dùng chung cho cả các trang**. Các bộ lọc áp dụng **đồng thời** (lấy phần giao nhau).

| Bộ lọc | Cách dùng |
|---|---|
| Năm | Chọn một hoặc nhiều năm. Tick **Chọn tất cả các năm** để chọn đủ 2023–2025 |
| Tháng, Quý | Chọn một hoặc nhiều tháng (1–12), quý (1–4) |
| Khoảng ngày | Chọn ngày bắt đầu và ngày kết thúc |
| Quốc gia | Lọc theo `country_code` |
| Trạng thái đơn hàng | completed, partially_refunded, cancelled, refunded |
| Kênh tiếp cận | organic, paid_search, paid_social, referral, affiliate |
| Phân khúc khách hàng | consumer, small_business, enterprise |

**Ví dụ**
- Xem riêng năm 2024: bỏ tick "Chọn tất cả các năm", chỉ chọn 2024.
- So sánh 2023 và 2024: chọn cả hai năm. Biểu đồ theo tháng sẽ vẽ **hai đường riêng**, không cộng gộp.
- Xem quý 4 của các năm: ở bộ lọc Quý chỉ giữ Quý 4.

**Lưu ý:** nếu bộ lọc quá hẹp và không còn đơn nào, trang sẽ báo "Không có đơn hàng bán thành công". Hãy bấm **↺ Đặt lại bộ lọc**.
        """)

    with tab3:
        st.markdown("""
**📊 Tổng quan kinh doanh**: 4 KPI (doanh thu thuần, số đơn bán thành công, số lượng sản phẩm, số khách hàng) kèm mức thay đổi so với năm trước; doanh thu và số đơn theo trạng thái; doanh thu từng năm và tốc độ tăng trưởng.

**📈 Xu hướng doanh thu**: chọn cấp độ **Ngày/Tháng/Quý/Năm** bằng ô chọn, chọn khoảng thời gian bằng ô ngày; bật/tắt đường **trung bình trượt**; biểu đồ so sánh doanh thu theo tháng giữa các năm (mỗi năm một đường).

**🌍 Theo quốc gia**: chọn nhiều quốc gia để so sánh; doanh thu, tỷ trọng, grouped bar theo năm; bảng thống kê; tăng trưởng và thay đổi tỷ trọng giữa năm đầu và năm cuối.

**🧾 Giá trị & cơ cấu đơn hàng**: kéo thanh **Top N** để xem các đơn lớn nhất; histogram và boxplot giá trị đơn; giá trị đơn, số sản phẩm, số dòng sản phẩm trung bình theo năm; Pivot Table quốc gia × phân khúc.

**🎯 Khách hàng & kênh**: doanh thu, số đơn, số khách hàng theo kênh tiếp cận và phân khúc; tỷ trọng, stacked bar, so sánh qua các năm.

**Bảng dữ liệu:** mở các mục **📋** để xem bảng chi tiết và bấm **⬇ Tải CSV** để tải về.
        """)

    with tab4:
        st.markdown("""
Mọi KPI, biểu đồ và bảng đều dùng **cùng một quy tắc**:

- **Doanh thu** = tổng `net_revenue` của các đơn **bán thành công**.
- **Đơn bán thành công** = đơn có `net_revenue > 0` và trạng thái **không** phải `cancelled` hoặc `refunded`. Đơn `partially_refunded` vẫn được tính nếu `net_revenue > 0`.
- **Tổng số đơn hàng** = tất cả trạng thái (đếm `order_id` duy nhất).
- **Số khách hàng** = số `customer_id` duy nhất.
- **Tăng trưởng** = (kỳ này − kỳ trước) / kỳ trước. Năm đầu tiên không có kỳ trước nên hiển thị **N/A**.
- **Tỷ trọng** = doanh thu của nhóm / tổng doanh thu trong phạm vi đang lọc.
- Dữ liệu **không nêu đơn vị tiền tệ**, nên Dashboard không gán đơn vị.
        """)

    with tab5:
        with st.expander("Vì sao đơn cancelled và refunded có doanh thu bằng 0?"):
            st.write("Đơn cancelled chưa được thanh toán. Đơn refunded được hoàn tiền toàn bộ, nên "
                     "net_revenue = gross_payment − refund_amount = 0. Hai loại đơn này vẫn được đếm "
                     "trong biểu đồ số đơn theo trạng thái nhưng không tính là bán thành công.")
        with st.expander("Vì sao KPI hiện 'N/A' ở mức tăng trưởng?"):
            st.write("Cần ít nhất 2 năm trong bộ lọc để so sánh. Hãy tick 'Chọn tất cả các năm' hoặc chọn thêm một năm.")
        with st.expander("Số liệu ở các trang khác nhau, tôi nên tin trang nào?"):
            st.write("Tất cả các trang dùng chung bộ lọc và quy tắc tính. Nếu số khác nhau, hãy kiểm tra "
                     "bộ lọc riêng ở đầu trang (ví dụ khoảng thời gian ở trang Xu hướng, quốc gia ở trang Quốc gia).")
        with st.expander("Tôi muốn đưa số liệu ra Excel/báo cáo thì làm thế nào?"):
            st.write("Mở mục 📋 dưới biểu đồ và bấm ⬇ Tải CSV. Có thể mở file CSV bằng Excel.")
        with st.expander("Biểu đồ trống hoặc có cảnh báo màu vàng?"):
            st.write("Bộ lọc đang loại hết dữ liệu. Bấm ↺ Đặt lại bộ lọc ở Sidebar.")
