"""
Flask E-commerce - Modern Clothing Store with Advanced Features
Run:
  python -m venv venv
  pip install flask
  python flask_clothing_store.py
Open http://127.0.0.1:5000
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from uuid import uuid4
import datetime
from functools import wraps
import json
import os
from werkzeug.utils import secure_filename
from database import db, init_db, Product, User, Order, Review, ReviewReply, ReviewLike, Voucher

app = Flask(__name__)
app.secret_key = "dev-secret-key-please-change-in-production"

# Upload configuration
UPLOAD_FOLDER = 'Images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clothing_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize database
init_db(app)

# Helper function to check allowed file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to serve uploaded images
@app.route('/Images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------- Helper Functions ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Vui lòng đăng nhập để tiếp tục', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session['user']['role'] != 'admin':
            flash('Bạn không có quyền truy cập trang này', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session['user']['role'] not in ['admin', 'staff']:
            flash('Đây là khu vực dành cho nhân viên', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def format_price(price):
    return f"{price:,.0f}đ".replace(',', '.')

def get_cart():
    return session.get('cart', [])

def get_wishlist():
    user_email = session.get('user', {}).get('email')
    if user_email:
        user = User.query.get(user_email)
        if user:
            return json.loads(user.wishlist) if user.wishlist else []
    return []

def calculate_cart_totals():
    cart = get_cart()
    subtotal = sum(item['price'] * item['qty'] for item in cart)
    
    # Calculate shipping
    shipping = 0 if subtotal >= 500000 else 30000
    
    # Calculate voucher discount
    voucher_discount = session.get('voucher_discount', 0)
    
    total = subtotal - voucher_discount + shipping
    return subtotal, shipping, voucher_discount, total

def get_featured_products():
    products = Product.query.filter_by(featured=True).all()
    return [p.to_dict() for p in products]

def get_best_sellers():
    products = Product.query.order_by(Product.sold.desc()).limit(8).all()
    return [p.to_dict() for p in products]

def get_categories():
    categories = db.session.query(Product.category).distinct().all()
    return [c[0] for c in categories]

# ---------- Context Processors ----------
@app.context_processor
def utility_processor():
    return {
        'now': datetime.datetime.now(),
        'wishlist_count': lambda: len(get_wishlist()),
        'cart_count': lambda: len(get_cart()),
        'format_price': format_price,
        'get_featured_products': get_featured_products,
        'get_best_sellers': get_best_sellers,
        'get_categories': get_categories,
        'get_wishlist': get_wishlist
    }

# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/products')
def products():
    category = request.args.get('category', '')
    search = request.args.get('q', '')
    price_range = request.args.get('price', '')
    sort = request.args.get('sort', '')
    
    # Filter products
    query = Product.query
    
    if category:
        query = query.filter_by(category=category)
    
    results = query.all()
    
    # 2. Lọc tìm kiếm bằng Python (Hỗ trợ tốt tiếng Việt "Á" và "á")
    if search:
        search_lower = search.lower() # Đổi từ khóa tìm kiếm về chữ thường
        # Chỉ giữ lại sản phẩm nào mà tên (đã đổi về chữ thường) có chứa từ khóa
        results = [p for p in results if search_lower in p.name.lower()]
    
    # 3. Chuyển đổi sang dictionary để hiển thị
    filtered_products = [p.to_dict() for p in results]
    
    return render_template('products.html', 
                         products=filtered_products,
                         category=category,
                         search=search,
                         price_range=price_range,
                         sort=sort)
    
    if price_range:
        if price_range == '0-200000':
            query = query.filter(Product.price <= 200000)
        elif price_range == '200000-500000':
            query = query.filter(Product.price >= 200000, Product.price <= 500000)
        elif price_range == '500000-999999999':
            query = query.filter(Product.price >= 500000)
    
    # Sort products
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'popular':
        query = query.order_by(Product.sold.desc())
    elif sort == 'rating':
        query = query.order_by(Product.rating.desc())
    elif sort == 'newest':
        query = query.order_by(Product.created_at.desc())
    
    filtered_products = [p.to_dict() for p in query.all()]
    
    return render_template('products.html', 
                         products=filtered_products,
                         category=category,
                         search=search,
                         price_range=price_range,
                         sort=sort)

@app.route('/sale')
def sale_products():
    products = Product.query.filter(Product.old_price > Product.price).all()
    sale_products = [p.to_dict() for p in products]
    return render_template('products.html', 
                         products=sale_products,
                         category='',
                         search='',
                         price_range='',
                         sort='',
                         page_title='Sản phẩm khuyến mãi')

@app.route('/product/<pid>')
def product_detail(pid):
    purchased_item = None
    product = Product.query.get(pid)
    if not product:
        flash('Sản phẩm không tồn tại', 'error')
        return redirect('/products')
    
    # Get related products
    related = Product.query.filter_by(category=product.category).filter(Product.id != pid).limit(4).all()
    related_products = [p.to_dict() for p in related]
    
    # Get reviews with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 5
    
    user_email = session.get('user', {}).get('email')
    reviews_query = Review.query.filter_by(product_id=pid).order_by(Review.created_at.desc())
    reviews_pagination = reviews_query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Calculate rating statistics
    all_reviews = Review.query.filter_by(product_id=pid).all()
    total_reviews = len(all_reviews)
    avg_rating = sum([r.rating for r in all_reviews]) / total_reviews if total_reviews > 0 else 0
    
    rating_stats = {
        '5': len([r for r in all_reviews if r.rating == 5]),
        '4': len([r for r in all_reviews if r.rating == 4]),
        '3': len([r for r in all_reviews if r.rating == 3]),
        '2': len([r for r in all_reviews if r.rating == 2]),
        '1': len([r for r in all_reviews if r.rating == 1]),
    }
    
    # Kiểm tra user đã mua sản phẩm này chưa
    can_review = False
    user_reviewed = False
    if user_email:
        reviews_count = Review.query.filter_by(product_id=pid, user_email=user_email).count()
        
        purchased_count = 0
        user_orders = Order.query.filter_by(user_email=user_email, status='completed').all()
        # Update code
        for order in user_orders:
                order_items = json.loads(order.items) if order.items else []
                for item in order_items:
                    if str(item.get('product_id')) == str(pid) or str(item.get('id')) == str(pid):
                        can_review = True
                        purchased_item = item
                        purchased_count += 1  
                        break
        

        user_reviewed = reviews_count >= purchased_count
        
        if not user_reviewed:
            user_orders = Order.query.filter_by(
                user_email=user_email,
                status='completed'
            ).all()

            for order in user_orders:
                order_items = json.loads(order.items) if order.items else []
                for item in order_items:
                    if str(item.get('product_id')) == str(pid):
                        can_review = True
                        purchased_item = item
                        break
                    if can_review:
                        break
    
    return render_template('product_detail.html', 
                         product=product.to_dict(), 
                         related_products=related_products,
                         reviews=[r.to_dict(user_email) for r in reviews_pagination.items],
                         reviews_pagination=reviews_pagination,
                         total_reviews=total_reviews,
                         avg_rating=round(avg_rating, 1),
                         rating_stats=rating_stats,
                         can_review=can_review,
                         user_reviewed=user_reviewed if user_email else False,
                         user_email=user_email,
                         purchased_item=purchased_item)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    if 'user' not in session:
        flash('Vui lòng đăng nhập để thêm vào giỏ hàng', 'error')
        return redirect('/login')
    
    pid = request.form.get('pid')
    color = request.form.get('color', 'Trắng')
    size = request.form.get('size', 'M')
    qty = int(request.form.get('qty', 1))
    
    product = Product.query.get(pid)
    if not product:
        flash('Sản phẩm không tồn tại', 'error')
        return redirect('/products')
    
    cart = get_cart()
    
    # Check if product already in cart with same color and size
    existing_item = next((item for item in cart if item['id'] == pid and 
                         item.get('color') == color and item.get('size') == size), None)
    
    if existing_item:
        existing_item['qty'] += qty
    else:
        cart.append({
            'id': pid,
            'name': product.name,
            'price': product.price,
            'image': product.image,
            'color': color,
            'size': size,
            'qty': qty
        })
    
    session['cart'] = cart
    flash('Đã thêm vào giỏ hàng', 'success')
    
    if request.referrer:
        return redirect(request.referrer)
    return redirect('/products')

@app.route('/update-cart', methods=['POST'])
def update_cart():
    pid = request.form.get('pid')
    color = request.form.get('color') # <--- Lấy thêm màu
    size = request.form.get('size')   # <--- Lấy thêm size
    action = request.form.get('action')
    
    cart = get_cart()
    
    # Tìm sản phẩm khớp cả ID, Màu và Size
    item = next((item for item in cart if item['id'] == pid and 
                 item.get('color') == color and item.get('size') == size), None)
    
    if item:
        if action == 'increase':
            item['qty'] += 1
        elif action == 'decrease' and item['qty'] > 1:
            item['qty'] -= 1
    
    session['cart'] = cart
    return redirect('/cart')

@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    pid = request.form.get('pid')
    color = request.form.get('color') # <--- Lấy thêm màu
    size = request.form.get('size')   # <--- Lấy thêm size
    
    cart = get_cart()
    
    # Giữ lại những sản phẩm KHÔNG trùng khớp (Xóa sản phẩm trùng khớp cả 3 yếu tố)
    cart = [item for item in cart if not (item['id'] == pid and 
                                        item.get('color') == color and 
                                        item.get('size') == size)]
    
    session['cart'] = cart
    flash('Đã xóa sản phẩm khỏi giỏ hàng', 'success')
    return redirect('/cart')

@app.route('/cart')
@login_required
def cart():
    cart = get_cart()
    subtotal, shipping, voucher_discount, total = calculate_cart_totals()
    voucher_code = session.get('voucher_code', '')
    
    return render_template('cart.html', 
                         cart=cart,
                         subtotal=subtotal,
                         shipping=shipping,
                         voucher_discount=voucher_discount,
                         total=total,
                         voucher_code=voucher_code)

@app.route('/apply-voucher', methods=['POST'])
@login_required
def apply_voucher():
    code = request.form.get('voucher', '').upper().strip()
    voucher = Voucher.query.filter_by(code=code, active=True).first()
    
    if not voucher:
        flash('Mã giảm giá không hợp lệ', 'error')
        return redirect('/cart')
    
    subtotal, _, _, _ = calculate_cart_totals()
    
    if subtotal < voucher.min_order:
        flash(f'Đơn hàng tối thiểu {format_price(voucher.min_order)} để sử dụng mã này', 'error')
        return redirect('/cart')
    
    if voucher.type == 'percent':
        discount = subtotal * voucher.discount / 100
    elif voucher.type == 'shipping':
        discount = voucher.discount
        # Set shipping to 0
        session['free_shipping'] = True
    else:
        discount = voucher.discount
    
    session['voucher_code'] = code
    session['voucher_discount'] = discount
    
    flash(f'Áp dụng mã giảm giá thành công', 'success')
    return redirect('/cart')

@app.route('/remove-voucher', methods=['POST'])
@login_required
def remove_voucher():
    session.pop('voucher_code', None)
    session.pop('voucher_discount', None)
    session.pop('free_shipping', None)
    flash('Đã xóa mã giảm giá', 'success')
    return redirect('/cart')

@app.route('/add-to-wishlist', methods=['POST'])
@login_required
def add_to_wishlist():
    data = request.get_json()
    pid = data.get('pid')
    
    user_email = session['user']['email']
    user = User.query.get(user_email)
    if user:
        wishlist = json.loads(user.wishlist) if user.wishlist else []
        if pid not in wishlist:
            wishlist.append(pid)
            user.wishlist = json.dumps(wishlist)
            db.session.commit()
    
    return jsonify({'success': True})

@app.route('/remove-from-wishlist', methods=['POST'])
@login_required
def remove_from_wishlist():
    data = request.get_json()
    pid = data.get('pid')
    
    user_email = session['user']['email']
    user = User.query.get(user_email)
    if user:
        wishlist = json.loads(user.wishlist) if user.wishlist else []
        if pid in wishlist:
            wishlist.remove(pid)
            user.wishlist = json.dumps(wishlist)
            db.session.commit()
    
    return jsonify({'success': True})

@app.route('/wishlist')
@login_required
def wishlist():
    wishlist_ids = get_wishlist()
    wishlist_products = [p.to_dict() for p in Product.query.filter(Product.id.in_(wishlist_ids)).all()]
    return render_template('wishlist.html', wishlist_products=wishlist_products)

# ---------- Review Routes ----------
@app.route('/product/<pid>/reviews')
def product_reviews(pid):
    """Get reviews for a product with pagination"""
    product = Product.query.get(pid)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    sort = request.args.get('sort', 'recent')  # recent, helpful, rating_high, rating_low
    
    query = Review.query.filter_by(product_id=pid)
    
    # Apply sorting
    if sort == 'helpful':
        query = query.order_by(Review.helpful_count.desc())
    elif sort == 'rating_high':
        query = query.order_by(Review.rating.desc())
    elif sort == 'rating_low':
        query = query.order_by(Review.rating.asc())
    else:  # recent
        query = query.order_by(Review.created_at.desc())
    
    reviews = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Calculate rating statistics
    all_reviews = Review.query.filter_by(product_id=pid).all()
    total_reviews = len(all_reviews)
    avg_rating = sum([r.rating for r in all_reviews]) / total_reviews if total_reviews > 0 else 0
    
    rating_stats = {
        '5': len([r for r in all_reviews if r.rating == 5]),
        '4': len([r for r in all_reviews if r.rating == 4]),
        '3': len([r for r in all_reviews if r.rating == 3]),
        '2': len([r for r in all_reviews if r.rating == 2]),
        '1': len([r for r in all_reviews if r.rating == 1]),
    }
    
    user_email = session.get('user', {}).get('email')
    
    return jsonify({
        'reviews': [r.to_dict(user_email) for r in reviews.items],
        'total': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'rating_stats': rating_stats,
        'has_next': reviews.has_next,
        'has_prev': reviews.has_prev,
        'page': page,
        'pages': reviews.pages
    })

@app.route('/product/<pid>/review', methods=['POST'])
@login_required
def add_review(pid):
    """Add a review for a product"""
    from database import ReviewReply
    
    product = Product.query.get(pid)
    if not product:
        return jsonify({'error': 'Sản phẩm không tồn tại'}), 404
    
    user_email = session['user']['email']
    
    # Check if user already reviewed this product
    current_reviews = Review.query.filter_by(product_id=pid, user_email=user_email).count()
    
    # 2. Đếm số lần mua thực tế
    purchased_count = 0
    user_orders = Order.query.filter_by(user_email=user_email, status='completed').all()
    for order in user_orders:
        order_items = json.loads(order.items)
        if any(str(item.get('product_id')) == str(pid) or str(item.get('id')) == str(pid) for item in order_items):
            purchased_count += 1
            
    # 3. Nếu số review đã bằng hoặc hơn số lần mua -> Chặn
    if current_reviews >= purchased_count:
        flash('Bạn đã đánh giá hết các lượt mua. Hãy mua thêm để tiếp tục!', 'warning')
        return redirect(url_for('product_detail', pid=pid))
    
    # Check if user has purchased this product
    user_orders = Order.query.filter_by(user_email=user_email, status='completed').all()
    has_purchased = False
    for order in user_orders:
        order_items = json.loads(order.items)
        # Check both 'product_id' and 'id' keys for compatibility
        if any(item.get('product_id') == pid or item.get('id') == pid for item in order_items):
            has_purchased = True
            break
    
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '')
    size = request.form.get('size', '')
    color = request.form.get('color', '')
    
    if not rating or rating < 1 or rating > 5:
        return jsonify({'error': 'Đánh giá phải từ 1 đến 5 sao'}), 400
    
    # Handle image uploads
    review_images = []
    if 'images' in request.files:
        files = request.files.getlist('images')
        for file in files[:5]:  # Maximum 5 images
            if file and allowed_file(file.filename):
                filename = f"review_{uuid4()}_{secure_filename(file.filename)}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                review_images.append(f"/Images/{filename}")
    
    review = Review(
        product_id=pid,
        user_email=user_email,
        rating=rating,
        comment=comment,
        images=json.dumps(review_images),
        size=size,
        color=color,
        verified_purchase=has_purchased,
        helpful_count=0
    )
    
    db.session.add(review)
    
    # Update product rating
    all_reviews = Review.query.filter_by(product_id=pid).all()
    all_reviews.append(review)
    new_avg_rating = sum([r.rating for r in all_reviews]) / len(all_reviews)
    product.rating = round(new_avg_rating, 1)
    product.reviews = len(all_reviews)
    
    db.session.commit()
    
    flash('Đánh giá của bạn đã được gửi thành công!', 'success')
    return redirect(url_for('product_detail', pid=pid))

@app.route('/review/<int:review_id>/reply', methods=['POST'])
@staff_required
def reply_review(review_id):
    """Admin/Staff reply to a review"""
    from database import ReviewReply
    
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Đánh giá không tồn tại'}), 404
    
    comment = request.form.get('comment', '')
    if not comment:
        return jsonify({'error': 'Nội dung phản hồi không được để trống'}), 400
    
    reply = ReviewReply(
        review_id=review_id,
        user_email=session['user']['email'],
        comment=comment
    )
    
    db.session.add(reply)
    db.session.commit()
    
    flash('Phản hồi đã được gửi thành công!', 'success')
    return jsonify({'success': True, 'reply': reply.to_dict()})

@app.route('/review/<int:review_id>/helpful', methods=['POST'])
@login_required
def mark_helpful(review_id):
    """Toggle like/unlike a review (1 user = 1 like max)"""
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Đánh giá không tồn tại'}), 404
    
    user_email = session['user']['email']
    
    # Kiểm tra user đã like chưa
    existing_like = ReviewLike.query.filter_by(review_id=review_id, user_email=user_email).first()
    
    if existing_like:
        # Unlike: xóa like
        db.session.delete(existing_like)
        db.session.commit()
        liked = False
    else:
        # Like: thêm like mới
        new_like = ReviewLike(review_id=review_id, user_email=user_email)
        db.session.add(new_like)
        db.session.commit()
        liked = True
    
    # Đếm tổng số like
    total_likes = ReviewLike.query.filter_by(review_id=review_id).count()
    
    return jsonify({
        'success': True,
        'helpful_count': total_likes,
        'liked': liked
    })

@app.route('/review/<int:review_id>/delete', methods=['POST'])
def delete_review(review_id):
    """Delete a review (only by owner or admin)"""
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Đánh giá không tồn tại'}), 404
    
    user_email = session.get('user', {}).get('email')
    user_role = session.get('user', {}).get('role')
    
    # Only review owner or admin can delete
    if review.user_email != user_email and user_role != 'admin':
        return jsonify({'error': 'Bạn không có quyền xóa đánh giá này'}), 403
    
    # Update product rating before deleting
    product = Product.query.get(review.product_id)
    if product:
        remaining_reviews = Review.query.filter_by(product_id=review.product_id).filter(Review.id != review_id).all()
        if remaining_reviews:
            new_avg_rating = sum([r.rating for r in remaining_reviews]) / len(remaining_reviews)
            product.rating = round(new_avg_rating, 1)
            product.reviews = len(remaining_reviews)
        else:
            product.rating = 0
            product.reviews = 0
    
    db.session.delete(review)
    db.session.commit()
    
    flash('Đánh giá đã được xóa', 'success')
    return jsonify({'success': True})

@app.route('/reply/<int:reply_id>/edit', methods=['POST'])
@staff_required
def edit_reply(reply_id):
    """Edit a review reply (admin/staff only)"""
    reply = ReviewReply.query.get(reply_id)
    if not reply:
        return jsonify({'error': 'Phản hồi không tồn tại'}), 404
    
    user_email = session['user']['email']
    user_role = session['user']['role']
    
    # Chỉ người tạo reply hoặc admin mới được sửa
    if reply.user_email != user_email and user_role != 'admin':
        return jsonify({'error': 'Bạn không có quyền sửa phản hồi này'}), 403
    
    comment = request.form.get('comment', '').strip()
    if not comment:
        return jsonify({'error': 'Nội dung phản hồi không được để trống'}), 400
    
    reply.comment = comment
    db.session.commit()
    
    return jsonify({'success': True, 'reply': reply.to_dict()})

@app.route('/reply/<int:reply_id>/delete', methods=['POST'])
@staff_required
def delete_reply(reply_id):
    """Delete a review reply (admin/staff only)"""
    reply = ReviewReply.query.get(reply_id)
    if not reply:
        return jsonify({'error': 'Phản hồi không tồn tại'}), 404
    
    user_email = session['user']['email']
    user_role = session['user']['role']
    
    # Chỉ người tạo reply hoặc admin mới được xóa
    if reply.user_email != user_email and user_role != 'admin':
        return jsonify({'error': 'Bạn không có quyền xóa phản hồi này'}), 403
    
    db.session.delete(reply)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = get_cart()
    if not cart:
        flash('Giỏ hàng trống', 'error')
        return redirect('/cart')
    
    if request.method == 'POST':
        # Process order
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        payment_method = request.form.get('payment_method')
        notes = request.form.get('notes', '')
        
        print(f"DEBUG: payment_method from form = {payment_method}")
        
        subtotal, shipping, voucher_discount, total = calculate_cart_totals()
        
        order = Order(
            id=str(uuid4()),
            user_email=session['user']['email'],
            items=json.dumps(cart),
            shipping_info=json.dumps({
                'name': name,
                'phone': phone,
                'address': address
            }),
            subtotal=subtotal,
            shipping=shipping,
            voucher_discount=voucher_discount,
            total=total,
            payment_method=payment_method,
            payment_status='pending' if payment_method in ['banking', 'momo', 'qr'] else 'cod',
            status='pending',
            notes=notes,
            created_at=datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        )
        
        db.session.add(order)
        db.session.commit()
        
        # Clear cart and voucher
        session.pop('cart', None)
        session.pop('voucher_code', None)
        session.pop('voucher_discount', None)
        session.pop('free_shipping', None)
        
        # Redirect to confirmation page for all payment methods
        flash('Đặt hàng thành công!', 'success')
        return redirect(f'/payment-confirmation/{order.id}')
    
    subtotal, shipping, voucher_discount, total = calculate_cart_totals()
    
    # Get user info for pre-filling form
    user_email = session['user']['email']
    user = User.query.get(user_email)
    user_info = user.to_dict() if user else {}
    
    return render_template('checkout.html',
                         cart=cart,
                         subtotal=subtotal,
                         shipping=shipping,
                         voucher_discount=voucher_discount,
                         total=total,
                         user_info=user_info)

@app.route('/payment/<order_id>')
@login_required
def payment_page(order_id):
    order = Order.query.get(order_id)
    if not order:
        flash('Đơn hàng không tồn tại', 'error')
        return redirect('/my-orders')
    
    # Check if user owns this order
    if order.user_email != session['user']['email']:
        flash('Bạn không có quyền xem đơn hàng này', 'error')
        return redirect('/my-orders')
    
    # Generate QR code URL for bank transfer
    bank_info = None
    if order.payment_method in ['banking', 'qr']:
        # VietQR format: https://img.vietqr.io/image/{BANK}-{ACCOUNT_NO}-{TEMPLATE}.png?amount={AMOUNT}&addInfo={INFO}
        bank_info = {
            'name': 'VietcomBank',
            'account': '0123456789',
            'account_name': 'FASHION STORE',
            'qr': f'https://img.vietqr.io/image/VCB-0123456789-compact.png?amount={order.total}&addInfo=ORDER{order.id[:8]}&accountName=FASHION STORE',
            'url': f'https://img.vietqr.io/image/VCB-0123456789-compact.png?amount={order.total}&addInfo=ORDER{order.id[:8]}'
        }
    
    return render_template('payment.html', order=order.to_dict(), bank_info=bank_info)

@app.route('/payment-confirmation/<order_id>')
@login_required
def payment_confirmation(order_id):
    order = Order.query.get(order_id)
    if not order:
        flash('Đơn hàng không tồn tại', 'error')
        return redirect('/my-orders')
    
    # Check if user owns this order
    if order.user_email != session['user']['email']:
        flash('Bạn không có quyền xem đơn hàng này', 'error')
        return redirect('/my-orders')
    
    return render_template('payment_confirmation.html', order=order.to_dict())

@app.route('/order/<order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get(order_id)
    if not order:
        flash('Đơn hàng không tồn tại', 'error')
        return redirect('/my-orders')
    
    # Check if user owns this order
    if order.user_email != session['user']['email'] and session['user']['role'] != 'admin':
        flash('Bạn không có quyền xem đơn hàng này', 'error')
        return redirect('/my-orders')
    
    order_dict = order.to_dict()
    
    # Kiểm tra sản phẩm nào chưa được đánh giá (nếu đơn hàng completed)
    if order.status == 'completed':
        user_email = session['user']['email']
        for item in order_dict['order_items']:
            product_id = item.get('product_id')
            if product_id:
                # Kiểm tra đã review chưa
                existing_review = Review.query.filter_by(
                    product_id=product_id,
                    user_email=user_email
                ).first()
                item['has_review'] = existing_review is not None
                item['review_id'] = existing_review.id if existing_review else None
            else:
                item['has_review'] = True  # Nếu không có product_id thì coi như đã review
    
    return render_template('order_detail.html', order=order_dict)

@app.route('/my-orders')
@login_required
def my_orders():
    user_email = session['user']['email']
    # Sort by created_at in descending order (newest first)
    orders = Order.query.filter_by(user_email=user_email).all()
    # Sort manually since created_at is a string
    user_orders = [o.to_dict() for o in orders]
    user_orders.sort(key=lambda x: x['created_at'], reverse=True)
    
    return render_template('my_orders.html', orders=user_orders)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        # Redirect to admin panel if already logged in as admin/staff
        if session['user']['role'] in ['admin', 'staff']:
            return redirect('/admin')
        return redirect('/')
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        user = User.query.get(email)
        if user and user.password == password:
            session['user'] = {
                'email': email,
                'name': user.name,
                'role': user.role
            }
            flash('Đăng nhập thành công', 'success')
            
            # Auto redirect admin/staff to admin panel
            if user.role in ['admin', 'staff']:
                return redirect('/admin')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect('/')
        else:
            flash('Email hoặc mật khẩu không đúng', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user' in session:
        return redirect('/')
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        
        if not all([email, password, confirm_password, name]):
            flash('Vui lòng điền đầy đủ thông tin bắt buộc', 'error')
        elif password != confirm_password:
            flash('Mật khẩu xác nhận không khớp', 'error')
        elif User.query.get(email):
            flash('Email đã tồn tại', 'error')
        else:
            user = User(
                email=email,
                password=password,
                role='user',
                name=name,
                phone=phone,
                address='',
                wishlist='[]',
                created_at=datetime.datetime.now()
            )
            db.session.add(user)
            db.session.commit()
            flash('Đăng ký thành công. Vui lòng đăng nhập.', 'success')
            return redirect('/login')
    
    return render_template('register.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # In a real app, you would send a password reset email
        flash('Nếu email tồn tại, chúng tôi đã gửi hướng dẫn đặt lại mật khẩu', 'success')
        return redirect('/login')
    
    return render_template('forgot_password.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất', 'success')
    return redirect('/')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_email = session['user']['email']
    user = User.query.get(user_email)
    
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        if name:
            user.name = name
            session['user']['name'] = name
        
        user.phone = phone
        user.address = address
        
        db.session.commit()
        flash('Cập nhật thông tin thành công', 'success')
        return redirect('/profile')
    
    return render_template('profile.html', user=user.to_dict() if user else {})

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    user_email = session['user']['email']
    user = User.query.get(user_email)
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_password or not new_password or not confirm_password:
        flash('Vui lòng điền đầy đủ thông tin', 'error')
    elif user.password != current_password:
        flash('Mật khẩu hiện tại không đúng', 'error')
    elif new_password != confirm_password:
        flash('Mật khẩu xác nhận không khớp', 'error')
    else:
        user.password = new_password
        db.session.commit()
        flash('Đổi mật khẩu thành công', 'success')
    
    return redirect('/profile')

@app.route('/admin')
@staff_required
def admin_dashboard():
    total_orders = Order.query.count()
    total_products = Product.query.count()
    total_users = User.query.count()
    
    # Calculate revenue
    completed_orders = Order.query.filter_by(status='completed').all()
    revenue = sum(order.total for order in completed_orders)
    
    # Calculate revenue by month and year
    from collections import defaultdict
    revenue_by_month = defaultdict(float)
    revenue_by_year = defaultdict(float)
    orders_by_month = defaultdict(int)
    orders_by_year = defaultdict(int)
    
    all_orders = Order.query.all()
    for order in all_orders:
        if order.created_at:
            try:
                # Parse date format: DD/MM/YYYY HH:MM
                date_parts = order.created_at.split(' ')[0].split('/')
                if len(date_parts) == 3:
                    day, month, year = date_parts
                    month_key = f"{month}/{year}"
                    year_key = year
                    
                    if order.status == 'completed':
                        revenue_by_month[month_key] += order.total
                        revenue_by_year[year_key] += order.total
                    
                    orders_by_month[month_key] += 1
                    orders_by_year[year_key] += 1
            except:
                pass
    
    # Sort by date (most recent first)
    sorted_months = sorted(revenue_by_month.items(), key=lambda x: (x[0].split('/')[1], x[0].split('/')[0]), reverse=True)[:12]
    sorted_years = sorted(revenue_by_year.items(), key=lambda x: x[0], reverse=True)
    
    print(f"DEBUG: Revenue by month: {dict(revenue_by_month)}")
    print(f"DEBUG: Revenue by year: {dict(revenue_by_year)}")
    print(f"DEBUG: Orders by year: {dict(orders_by_year)}")
    print(f"DEBUG: Sorted years: {sorted_years}")
    
    recent_orders = [o.to_dict() for o in Order.query.limit(5).all()]
    recent_orders.sort(key=lambda x: x['created_at'], reverse=True)
    
    return render_template('admin/dashboard.html',
                         total_orders=total_orders,
                         total_products=total_products,
                         total_users=total_users,
                         revenue=revenue,
                         revenue_by_month=sorted_months,
                         revenue_by_year=sorted_years,
                         orders_by_month=orders_by_month,
                         orders_by_year=orders_by_year,
                         recent_orders=recent_orders)

@app.route('/admin/orders')
@staff_required
def admin_orders():
    orders = [o.to_dict() for o in Order.query.all()]
    orders.sort(key=lambda x: x['created_at'], reverse=True)
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/create-order', methods=['GET', 'POST'])
@admin_required
def admin_create_order():
    if request.method == 'GET':
        # Get all customers for dropdown
        customers = User.query.filter_by(role='user').all()
        products = Product.query.all()
        return render_template('admin/create_order.html', customers=customers, products=products)
    
    if request.method == 'POST':
        # Get form data
        customer_email = request.form.get('customer_email')
        customer_name = request.form.get('customer_name')
        customer_phone = request.form.get('customer_phone')
        customer_address = request.form.get('customer_address')
        payment_method = request.form.get('payment_method')
        payment_status = request.form.get('payment_status')
        notes = request.form.get('notes', '')
        
        # Get products from form (JSON array)
        import json
        products_json = request.form.get('products')
        if not products_json:
            flash('Vui lòng thêm ít nhất 1 sản phẩm', 'error')
            return redirect('/admin/create-order')
        
        try:
            cart_items = json.loads(products_json)
        except:
            flash('Dữ liệu sản phẩm không hợp lệ', 'error')
            return redirect('/admin/create-order')
        
        # Calculate totals
        subtotal = sum(item['price'] * item['qty'] for item in cart_items)
        shipping = 30000 if subtotal < 500000 else 0
        total = subtotal + shipping
        
        # Create order
        order = Order(
            id=str(uuid4()),
            user_email=customer_email,
            items=json.dumps(cart_items),
            shipping_info=json.dumps({
                'name': customer_name,
                'phone': customer_phone,
                'address': customer_address
            }),
            subtotal=subtotal,
            shipping=shipping,
            voucher_discount=0,
            total=total,
            payment_method=payment_method,
            payment_status=payment_status,
            status='pending',
            notes=notes,
            created_at=datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        )
        
        db.session.add(order)
        db.session.commit()
        
        flash(f'Đã tạo đơn hàng #{order.id[:8]} thành công', 'success')
        return redirect('/admin/orders')
    
    # GET request - show form
    products = [p.to_dict() for p in Product.query.all()]
    customers = User.query.filter_by(role='user').all()
    return render_template('admin/create_order.html', products=products, customers=customers)

@app.route('/admin/products')
@staff_required
def admin_products():
    products = [p.to_dict() for p in Product.query.all()]
    return render_template('admin/products.html', products=products)

@app.route('/admin/update-order-status', methods=['POST'])
@staff_required
def update_order_status():
    order_id = request.form.get('order_id')
    status = request.form.get('status')
    
    order = Order.query.get(order_id)
    if order:
        order.status = status
        db.session.commit()
        flash('Cập nhật trạng thái đơn hàng thành công', 'success')
    
    return redirect('/admin/orders')

@app.route('/templates/<template_name>')
def serve_template(template_name):
    return render_template(template_name)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

@app.route('/payment/complete/<order_id>', methods=['POST'])
@login_required
def payment_complete(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success':False}),404
    order.payment_status = 'paid'
    order.status = 'completed'
    db.session.commit()
    return jsonify({'success':True, 'redirect': url_for('home')})

@app.route('/admin/add-product', methods=['GET', 'POST'])
@staff_required
def admin_add_product():
    if request.method == 'POST':
        # Handle image upload
        image_url = ''
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                # Generate unique filename
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{uuid4().hex[:8]}{ext}"
                
                # Save file
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                image_url = f"/Images/{unique_filename}"
        
        # If no file uploaded, use URL from input
        if not image_url:
            image_url = request.form.get('image', '')
        
        # Get form values with proper handling of empty strings
        try:
            price = int(request.form.get('price', '0') or '0')
            old_price = int(request.form.get('old_price', '0') or '0')
            stock = int(request.form.get('stock', '0') or '0')
        except ValueError:
            flash('Giá và số lượng phải là số hợp lệ', 'error')
            return redirect('/admin/add-product')
        
        product = Product(
            id=str(uuid4()),
            name=request.form['name'],
            price=price,
            old_price=old_price,
            category=request.form.get('category', ''),
            image=image_url,
            images=json.dumps([image_url]),
            description=request.form.get('description', ''),
            stock=stock,
            sizes=json.dumps([s.strip() for s in request.form.get('sizes', '').split(',') if s.strip()]),
            colors=json.dumps([c.strip() for c in request.form.get('colors', '').split(',') if c.strip()]),
            color_images=json.dumps({}),
            rating=0,
            reviews=0,
            sold=0,
            featured=bool(request.form.get('featured'))
        )
        db.session.add(product)
        db.session.commit()
        flash('Đã thêm sản phẩm', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin/add_product.html')

# Admin User Management
@app.route('/admin/users')
@admin_required
def admin_users():
    role_filter = request.args.get('role', 'all')
    
    if role_filter == 'all':
        users = User.query.all()
    else:
        users = User.query.filter_by(role=role_filter).all()
    
    all_count = User.query.count()
    admin_count = User.query.filter_by(role='admin').count()
    staff_count = User.query.filter_by(role='staff').count()
    user_count = User.query.filter_by(role='user').count()
    
    return render_template('admin/users.html', 
                         users=[u.to_dict() for u in users],
                         role=role_filter,
                         all_count=all_count,
                         admin_count=admin_count,
                         staff_count=staff_count,
                         user_count=user_count)

@app.route('/admin/add-user', methods=['GET', 'POST'])
@admin_required
def admin_add_user():
    if request.method == 'POST':
        email = request.form.get('email')
        
        if User.query.get(email):
            flash('Email đã tồn tại', 'error')
            return redirect('/admin/add-user')
        
        user = User(
            email=email,
            password=request.form.get('password'),
            name=request.form.get('name'),
            phone=request.form.get('phone', ''),
            address=request.form.get('address', ''),
            role=request.form.get('role', 'user'),
            wishlist='[]',
            created_at=datetime.datetime.now()
        )
        db.session.add(user)
        db.session.commit()
        flash('Đã thêm tài khoản', 'success')
        return redirect('/admin/users')
    
    return render_template('admin/user_form.html', user=None)

@app.route('/admin/edit-user/<email>', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(email):
    user = User.query.get(email)
    if not user:
        flash('Tài khoản không tồn tại', 'error')
        return redirect('/admin/users')
    
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.phone = request.form.get('phone', '')
        user.address = request.form.get('address', '')
        user.role = request.form.get('role', 'user')
        
        new_password = request.form.get('new_password')
        if new_password:
            user.password = new_password
        
        db.session.commit()
        flash('Đã cập nhật tài khoản', 'success')
        return redirect('/admin/users')
    
    return render_template('admin/user_form.html', user=user.to_dict())

@app.route('/admin/delete-user', methods=['POST'])
@admin_required
def admin_delete_user():
    email = request.form.get('email')
    
    # Prevent deleting own account
    if email == session['user']['email']:
        flash('Không thể xóa tài khoản của chính mình', 'error')
        return redirect('/admin/users')
    
    user = User.query.get(email)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('Đã xóa tài khoản', 'success')
    
    return redirect('/admin/users')

# Admin Product Management
@app.route('/admin/edit-product/<product_id>', methods=['GET', 'POST'])
@staff_required
def admin_edit_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash('Sản phẩm không tồn tại', 'error')
        return redirect('/admin/products')
    
    if request.method == 'POST':
        # Handle image upload
        image_url = product.image  # Keep existing image by default
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                # Generate unique filename
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{uuid4().hex[:8]}{ext}"
                
                # Save file
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                image_url = f"/Images/{unique_filename}"
        
        # If no file uploaded, check if URL was changed
        if image_url == product.image:
            new_url = request.form.get('image', '')
            if new_url:
                image_url = new_url
        
        # Handle numeric fields safely
        try:
            price = int(request.form.get('price', '0') or '0')
            old_price = int(request.form.get('old_price', '0') or '0')
            stock = int(request.form.get('stock', '0') or '0')
        except ValueError:
            flash('Giá và số lượng phải là số hợp lệ', 'error')
            return redirect(f'/admin/edit-product/{product_id}')
        
        product.name = request.form.get('name')
        product.price = price
        product.old_price = old_price
        product.category = request.form.get('category', '')
        product.image = image_url
        product.images = json.dumps([image_url])
        product.description = request.form.get('description', '')
        product.stock = stock
        product.sizes = json.dumps([s.strip() for s in request.form.get('sizes', '').split(',') if s.strip()])
        product.colors = json.dumps([c.strip() for c in request.form.get('colors', '').split(',') if c.strip()])
        if not product.color_images:
            product.color_images = json.dumps({})
        product.featured = bool(request.form.get('featured'))
        
        db.session.commit()
        flash('Đã cập nhật sản phẩm', 'success')
        return redirect('/admin/products')
    
    return render_template('admin/edit_product.html', product=product.to_dict())

@app.route('/admin/delete-product', methods=['POST'])
@admin_required
def admin_delete_product():
    product_id = request.form.get('product_id')
    product = Product.query.get(product_id)
    
    if product:
        db.session.delete(product)
        db.session.commit()
        flash('Đã xóa sản phẩm', 'success')
    
    return redirect('/admin/products')

@app.route('/admin/delete-order', methods=['POST'])
@admin_required
def admin_delete_order():
    order_id = request.form.get('order_id')
    order = Order.query.get(order_id)
    
    if order:
        db.session.delete(order)
        db.session.commit()
        flash(f'Đã xóa đơn hàng #{order_id[:8]}', 'success')
    else:
        flash('Đơn hàng không tồn tại', 'error')
    
    return redirect('/admin/orders')

@app.route('/admin/edit-order/<order_id>', methods=['GET', 'POST'])
@staff_required
def admin_edit_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        flash('Đơn hàng không tồn tại', 'error')
        return redirect('/admin/orders')
    
    if request.method == 'POST':
        # Update shipping info
        shipping_info = json.loads(order.shipping_info) if order.shipping_info else {}
        shipping_info['name'] = request.form.get('customer_name')
        shipping_info['phone'] = request.form.get('customer_phone')
        shipping_info['address'] = request.form.get('customer_address')
        
        order.shipping_info = json.dumps(shipping_info)
        order.payment_method = request.form.get('payment_method')
        order.payment_status = request.form.get('payment_status')
        order.status = request.form.get('status')
        order.notes = request.form.get('notes', '')
        
        # Update products if provided
        products_json = request.form.get('products')
        if products_json:
            try:
                cart_items = json.loads(products_json)
                order.items = products_json
                
                # Recalculate totals
                subtotal = sum(item['price'] * item['qty'] for item in cart_items)
                shipping = 0 if subtotal >= 500000 else 30000
                total = subtotal + shipping - order.voucher_discount
                
                order.subtotal = subtotal
                order.shipping = shipping
                order.total = total
            except:
                flash('Dữ liệu sản phẩm không hợp lệ', 'error')
                return redirect(f'/admin/edit-order/{order_id}')
        
        db.session.commit()
        flash(f'Đã cập nhật đơn hàng #{order_id[:8]}', 'success')
        return redirect('/admin/orders')
    
    # GET request
    order_dict = order.to_dict()
    products = [p.to_dict() for p in Product.query.all()]
    return render_template('admin/edit_order.html', order=order_dict, products=products)

if __name__ == '__main__':
    print("=" * 50)
    print("Flask Clothing Store Starting...")
    print("Server will be available at: http://127.0.0.1:5000")
    print("Press CTRL+C to stop the server")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
