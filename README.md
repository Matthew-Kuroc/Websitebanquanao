# 🛍️ Fashion Store - Đồ Án Website Bán Quần Áo

Đây là đồ án xây dựng website thương mại điện tử kinh doanh quần áo thời trang, được xây dựng bằng ngôn ngữ **Python** và **Flask Framework**.

## 🚀 Giới thiệu
Dự án mô phỏng một quy trình mua sắm trọn vẹn từ phía Khách hàng (xem, lọc, mua, đánh giá) đến phía Quản trị viên (quản lý đơn hàng, sản phẩm, doanh thu).

**Công nghệ sử dụng:**
* **Backend:** Python, Flask, SQLAlchemy (SQLite).
* **Frontend:** HTML5, Jinja2, TailwindCSS (CDN), JavaScript.
* **Database:** SQLite (Tự động khởi tạo).

---

## ✨ Tính năng chính

### 1. Dành cho Khách hàng (User)
* 🛒 **Mua sắm:** Thêm vào giỏ hàng, cập nhật số lượng, xóa sản phẩm.
* 💳 **Thanh toán:** Giả lập thanh toán COD, Chuyển khoản, MoMo (có mã QR).
* ❤️ **Yêu thích:** Thêm/Xóa sản phẩm khỏi danh sách yêu thích (Wishlist).
* ⭐ **Đánh giá:** Bình luận và chấm sao sản phẩm đã mua (có upload ảnh thực tế).
* 🔍 **Tìm kiếm & Lọc:** Tìm theo tên, lọc theo giá, danh mục, sắp xếp (bán chạy, giá tăng/giảm).
* 👤 **Tài khoản:** Đăng ký, Đăng nhập, Quản lý đơn hàng cá nhân.

### 2. Dành cho Quản trị viên (Admin) & Nhân viên (Staff)
* 📊 **Dashboard:** Xem thống kê doanh thu, số lượng đơn hàng, biểu đồ tăng trưởng.
* 📦 **Quản lý Sản phẩm:** Thêm, Sửa, Xóa sản phẩm (Hỗ trợ upload nhiều ảnh theo màu sắc).
* 📝 **Quản lý Đơn hàng:** Xem chi tiết, cập nhật trạng thái đơn (Đang giao, Hoàn thành...).
* 💬 **Phản hồi:** Trả lời bình luận của khách hàng.
* 🔐 **Phân quyền:** * **Admin:** Toàn quyền (Quản lý cả tài khoản User/Staff).
    * **Staff:** Chỉ quản lý bán hàng, không được xóa dữ liệu quan trọng.
