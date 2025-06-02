from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from app import db
from app.models import User, Product, Cart, Order, Delivery, ContactMessage
from sqlalchemy import func, cast, Integer

main = Blueprint('main', __name__)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = 'customer'

        #  Check for @ and .com
        if '@' not in email or '.com' not in email:
            flash('Please enter a valid email address (must include @ and .com)', 'danger')
            return redirect(url_for('main.register'))

        #  Set admin request only if email ends with @swin.com
        is_admin_approved = False
        admin_requested = False
        if email.endswith('@swin.com'):
            admin_requested = True
        else:
            flash('Only @swin.com users can request admin approval.', 'info')

        new_user = User(
            name=name,
            email=email,
            password=password,
            role=role,
            is_admin_approved=is_admin_approved,
            admin_requested=admin_requested
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created. Please login.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Invalid login.', 'danger')
    return render_template('login.html')

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'owner':
        return redirect(url_for('main.admin_dashboard'))
    return render_template('dashboard.html')

@main.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'owner' or not current_user.is_admin_approved:
        flash("Access denied: You are not an approved admin.", "danger")
        return redirect(url_for('main.dashboard'))

    
    products = Product.query.order_by(Product.is_active.desc()).all() # active products listed first
    unapproved_users = User.query.filter(
    User.role == 'customer',
    User.is_admin_approved == False,
    User.admin_requested == True,
    User.email.ilike('%@swin.com')
).all()

    approved_admins = User.query.filter_by(role='owner', is_admin_approved=True).all()

    return render_template(
        'admin_dashboard.html',
        products=products,
        unapproved_users=unapproved_users,
        approved_admins=approved_admins
    )




@main.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.role != 'owner':
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        desc = request.form['description']
        image = request.form['image_url']
        category = request.form['category']
        product = Product(name=name, price=price, description=desc, image_url=image, category=category)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('main.admin_dashboard'))
    return render_template('add_product.html')

@main.route('/sales_report', methods=['GET', 'POST'])
@login_required
def sales_report():
    if current_user.role != 'owner':
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        todays_date = date.today() # generates todays date

        sales_report = db.session.query(
            # casted back to Integer from decimal returned from sum()
            Order.product_id, Product.name, cast(func.sum(Order.quantity), Integer).label('quantity_sold'), Product.price 
            ).join(Product, Order.product_id == Product.id
            ).filter(Order.transaction_date >= start_date, Order.transaction_date <= end_date
            ).group_by(Order.product_id).all()

        if sales_report == []:  # no sales within that period
            flash(f"No sales were found in the specified time period of '{start_date}' to '{end_date}'", "danger")
            return redirect(url_for('main.admin_dashboard'))
        else:    
            total_qty = sum(sales.quantity_sold for sales in sales_report)
            total_sales = sum(sales.quantity_sold * sales.price for sales in sales_report)

            return render_template(
                'sales_report.html', 
                sales_report=sales_report, 
                start_date=start_date, 
                end_date=end_date, 
                todays_date=todays_date,
                total_qty=total_qty,
                total_sales=total_sales
                )
    
    return render_template('admin_dashboard.html')


@main.route('/deactivate_product/<int:product_id>')
@login_required
def deactivate_product(product_id):
    if current_user.role != 'owner':
        return redirect(url_for('main.dashboard'))
    
    product = Product.query.get(product_id)
    product.is_active = False # changes product to inactive to preserve item history

    db.session.commit()
    flash("Product has been deactivated!", "success")
    return redirect(url_for('main.admin_dashboard'))

@main.route('/activate_product/<int:product_id>')
@login_required
def activate_product(product_id):
    if current_user.role != 'owner':
        return redirect(url_for('main.dashboard'))
    
    product = Product.query.get(product_id)
    product.is_active = True # changes product to inactive to preserve item history

    db.session.commit()
    flash("Product has been re-activated!", "success")
    return redirect(url_for('main.admin_dashboard'))

@main.route('/products')
def product_list():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    search = request.args.get('q', '').strip()
    selected_category = request.args.get('category', '').strip()

    query = Product.query

    if selected_category:
        # Category overrides search completely
        query = query.filter(Product.category == selected_category)
    elif search:
        # Only use search if category isn't selected
        query = query.filter(Product.name.ilike(f"%{search}%"))

    products = query.paginate(page=page, per_page=per_page)

    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories if c[0] is not None]

    return render_template(
        'product_list.html',
        products=products,
        categories=categories,
        selected_category=selected_category
    )





@main.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    existing_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if existing_item:
        existing_item.quantity += 1
    else:
        new_item = Cart(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(new_item)

    db.session.commit()
    flash("Product added to cart successfully!", "success")
    return redirect(url_for('main.product_list'))

@main.route('/cart')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    return render_template('cart.html', cart_items=cart_items)


@main.route('/delete_from_cart/<int:product_id>')
@login_required
def delete_from_cart(product_id):
    existing_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    db.session.delete(existing_item)

    db.session.commit()
    flash("Product removed from cart!", "success")
    return redirect(url_for('main.cart'))

@main.route('/checkout', methods=['GET'])
@login_required
def checkout():
    return render_template('checkout.html')

@main.route('/process_checkout', methods=['POST'])
@login_required
def process_checkout():
    address = request.form.get('address')
    city = request.form.get('city')
    postal_code = request.form.get('postal_code')
    card_name = request.form.get('card_name')
    card_number = request.form.get('card_number')

    last_4=card_number[:4] # last 4 numbers of the card is in plaintext

    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    
    transaction_date=datetime.now().replace(microsecond=0) # set timestamp upon processing checkout and remove microsecond for queries

    for item in cart_items:
        order = Order(user_id=current_user.id, product_id=item.product_id, quantity=item.quantity, transaction_date=transaction_date)
        db.session.add(order)
        db.session.flush()  # gets order.id before commit

        # save delivery info for this order
        delivery = Delivery(
            user_id=current_user.id,
            order_id=order.id,
            address=address,
            city=city,
            postal_code=postal_code,
            card_name=card_name,
            card_number=last_4, # last 4 of the card number is stored for best security practices
        )
        db.session.add(delivery)
        db.session.delete(item)

    db.session.commit()

    order_details = Order.query.filter_by(user_id=current_user.id, transaction_date=transaction_date).all() # filter based on user id and transaction date
    total_qty = sum(order.quantity for order in order_details) # total quantity of order
    total_price = sum(order.quantity * order.product.price for order in order_details) # total price of order

    flash("Order placed successfully!", "success")
    return render_template('invoice.html', order_details=order_details, total_qty=total_qty, total_price=total_price, transaction_date=transaction_date)

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        message = ContactMessage(
            name=request.form['name'],
            email=request.form['email'],
            subject=request.form['subject'],
            message=request.form['message']
        )
        db.session.add(message)
        db.session.commit()
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('main.contact'))
    return render_template('contact.html')

@main.route('/')
def index():
    # Get featured products (newest products)
    featured_products = Product.query.order_by(Product.id.desc()).limit(4).all()

    # Get top sellers (most ordered products)
    top_sellers = db.session.query(Product, db.func.count(Order.id).label('order_count'))\
    .join(Order)\
    .group_by(Product.id)\
    .order_by(db.text('order_count DESC'))\
    .limit(4)\
    .all()
    top_sellers = [product for product, _ in top_sellers]

    return render_template('index.html',
                           featured_products=featured_products,
                           top_sellers=top_sellers)

@main.route('/admin/messages')
@login_required
def admin_messages():
    if current_user.role != 'owner':
        return redirect(url_for('main.dashboard'))
    messages = ContactMessage.query.filter_by(status='unread').order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin_messages.html', messages=messages)
@main.route('/approve_admin/<int:user_id>', methods=['POST'])
@login_required
def approve_admin(user_id):
    if current_user.role != 'owner' or not current_user.is_admin_approved:
        flash("Unauthorized", "danger")
        return redirect(url_for('main.dashboard'))

    user = User.query.get_or_404(user_id)
    user.role = 'owner'
    user.is_admin_approved = True
    db.session.commit()
    flash(f"{user.name} is now an approved admin!", "success")
    return redirect(url_for('main.admin_dashboard'))
@main.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if current_user.role != 'owner' or not current_user.is_admin_approved:
        return redirect(url_for('main.dashboard'))

    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.price = float(request.form['price'])
        product.description = request.form['description']
        product.image_url = request.form['image_url']
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('main.admin_dashboard'))

    return render_template('edit_product.html', product=product)


@main.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if current_user.role != 'owner' or not current_user.is_admin_approved:
        return redirect(url_for('main.dashboard'))

    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted!', 'success')
    return redirect(url_for('main.admin_dashboard'))
@main.route('/demote_admin/<int:user_id>', methods=['POST'])
@login_required
def demote_admin(user_id):
    if current_user.role != 'owner' or not current_user.is_admin_approved:
        return redirect(url_for('main.dashboard'))

    user = User.query.get_or_404(user_id)
    user.role = 'customer'
    user.is_admin_approved = False
    db.session.commit()
    flash(f"{user.name} has been demoted to customer.", "warning")
    return redirect(url_for('main.admin_dashboard'))

@main.route('/update_product/<int:product_id>', methods=['POST'])
@login_required
def update_product(product_id):
    if current_user.role != 'owner' or not current_user.is_admin_approved:
        flash("Unauthorized", "danger")
        return redirect(url_for('main.dashboard'))

    product = Product.query.get_or_404(product_id)
    product.name = request.form['name']
    product.price = float(request.form['price'])
    product.description = request.form['description']
    db.session.commit()

    flash('Product updated successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))
@main.route('/mark_message_read/<int:message_id>', methods=['POST'])
@login_required
def mark_message_read(message_id):
    if current_user.role != 'owner':
        return redirect(url_for('main.dashboard'))

    msg = ContactMessage.query.get_or_404(message_id)
    msg.status = 'read'
    db.session.commit()
    flash("Message marked as read.", "info")
    return redirect(url_for('main.admin_messages'))
@main.route('/delete_user_request/<int:user_id>', methods=['POST'])
@login_required
def delete_user_request(user_id):
    if current_user.role != 'owner' or not current_user.is_admin_approved:
        flash("Unauthorized", "danger")
        return redirect(url_for('main.dashboard'))

    user = User.query.get_or_404(user_id)

    if user.role == 'customer' and not user.is_admin_approved:
        user.admin_requested = False 
        db.session.commit()
        flash(f"Admin request from {user.name} has been removed.", "info")
    else:
        flash("This user isn't a pending admin request.", "warning")

    return redirect(url_for('main.admin_dashboard'))

