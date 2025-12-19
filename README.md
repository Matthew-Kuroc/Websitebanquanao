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

---

## 🛠️ Hướng dẫn Cài đặt & Chạy (Cho thành viên nhóm)

Để chạy dự án này trên máy cá nhân, hãy làm theo các bước sau:

### Bước 1: Cài đặt Python
Đảm bảo máy tính đã cài Python (phiên bản 3.8 trở lên).

### Bước 2: Tải thư viện
Mở Terminal (hoặc CMD) tại thư mục dự án và chạy lệnh:
```bash
pip install -r requirements.txt
Bước 3: Chạy ứng dụngChạy lệnh sau để khởi động server:Bashpython flask_clothing_store.py
Bước 4: Truy cậpMở trình duyệt và vào địa chỉ: http://127.0.0.1:5000Lưu ý: Lần chạy đầu tiên, hệ thống sẽ tự động tạo file database clothing_store.db và nạp sẵn dữ liệu mẫu (Sản phẩm, User test).🔑 Tài khoản Demo (Dùng để Test)Dưới đây là các tài khoản đã được tạo sẵn trong hệ thống:Vai tròEmailMật khẩuQuyền hạnAdminadmin@example.comadmin123Full quyền (Quản lý User, Xóa đơn...)Staffstaff@example.comstaff123Quản lý đơn hàng, Sản phẩmUsernguyen.van.a@gmail.comuser123Mua hàng, Đánh giá📂 Cấu trúc thư mụcflask_clothing_store.py: File chính để chạy ứng dụng.database.py: Định nghĩa cơ sở dữ liệu và dữ liệu mẫu.templates/: Chứa các file giao diện HTML.admin/: Giao diện trang quản trị.Images/: Chứa ảnh sản phẩm và ảnh đánh giá (Upload).instance/: Chứa file clothing_store.db (Database).
