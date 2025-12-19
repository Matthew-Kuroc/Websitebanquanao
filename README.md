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

Để chạy dự án này trên máy cá nhân, hãy làm theo đúng trình tự sau:

### Bước 1: Cài đặt Python
Đảm bảo máy tính của bạn đã cài đặt Python (khuyên dùng phiên bản **3.8** trở lên).
* Kiểm tra bằng lệnh: `python --version`

### Bước 2: Tải thư viện
Mở Terminal (hoặc CMD) ngay tại thư mục chứa dự án và chạy lệnh sau để cài đặt các gói cần thiết:
```bash
pip install -r requirements.txt
(Nếu chưa có file requirements.txt, hãy chạy lệnh thủ công: pip install Flask Flask-SQLAlchemy)Bước 3: Khởi chạy ứng dụngSau khi cài xong thư viện, hãy chạy lệnh sau để khởi động Server:Bashpython flask_clothing_store.py
(Nếu thấy dòng chữ "Running on http://127.0.0.1:5000" hiện lên nghĩa là đã thành công)Bước 4: Truy cập WebsiteMở trình duyệt web (Chrome, Edge, Cốc Cốc...) và truy cập vào địa chỉ:http://127.0.0.1:5000⚠️ Lưu ý quan trọng: Trong lần chạy đầu tiên, hệ thống sẽ tự động tạo file database (clothing_store.db) và nạp sẵn dữ liệu mẫu (Sản phẩm, Admin, User test...) nên bạn không cần làm gì thêm.🔑 Tài khoản Demo (Dùng để Test)Dưới đây là các tài khoản đã được tạo sẵn trong hệ thống để nhóm tiện kiểm tra:Vai tròEmailMật khẩuQuyền hạnAdminadmin@example.comadmin123Full quyền (Quản lý User, Xóa đơn...)Staffstaff@example.comstaff123Quản lý đơn hàng, Sản phẩmUsernguyen.van.a@gmail.comuser123Mua hàng, Đánh giá📂 Cấu trúc thư mụcflask_clothing_store.py: File chính (Controller) để chạy ứng dụng.database.py: File cấu hình Database và dữ liệu mẫu (Models).templates/: Thư mục chứa giao diện (HTML).admin/: Giao diện dành riêng cho trang quản trị.Images/: Thư mục chứa ảnh sản phẩm và ảnh đánh giá.instance/: Thư mục chứa file Database (clothing_store.db).
