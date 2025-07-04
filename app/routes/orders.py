from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app.models.order import Order
from app.models.customer import Customer
from app.models.lens_type import LensType
from app.models.lens_cut_type import LensCutType
from app.models.order_lens import OrderLens
from app.models.cashbox import CashBox, CashBoxTransaction
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.sql import or_
from app.forms.order import OrderForm
from app.forms.order_expense import OrderExpenseForm
from app.models.expense import Expense

bp = Blueprint('orders', __name__)

def distribute_income_to_cashboxes(order):
    """توزیع درآمد سفارش به صندوق‌ها"""
    customer = Customer.query.get(order.customer_id)

    # دریافت یا ایجاد صندوق‌ها
    cashbox_a = CashBox.query.filter_by(name='A').first()
    if not cashbox_a:
        cashbox_a = CashBox(name='A', balance=0.0)
        db.session.add(cashbox_a)
        db.session.flush()

    cashbox_b = CashBox.query.filter_by(name='B').first()
    if not cashbox_b:
        cashbox_b = CashBox(name='B', balance=0.0)
        db.session.add(cashbox_b)
        db.session.flush()

    if customer.is_vip:
        # مشتری VIP: 80000 تومان به ازای هر عدسی به صندوق A، مابقی به صندوق B
        total_lenses = sum(lens.quantity for lens in order.lenses)
        amount_to_a = total_lenses * 80000
        amount_to_b = order.total_amount - amount_to_a
        if amount_to_b < 0:
            amount_to_a = order.total_amount
            amount_to_b = 0
        cashbox_a.balance += amount_to_a
        if amount_to_a > 0:
            transaction_a = CashBoxTransaction(
                cashbox_id=cashbox_a.id,
                amount=amount_to_a,
                transaction_type='income',
                description=f'درآمد سفارش {order.order_number} - {customer.full_name} (VIP)',
                reference_type='order',
                reference_id=order.id
            )
            db.session.add(transaction_a)
        if amount_to_b > 0:
            cashbox_b.balance += amount_to_b
            transaction_b = CashBoxTransaction(
                cashbox_id=cashbox_b.id,
                amount=amount_to_b,
                transaction_type='income',
                description=f'درآمد سفارش {order.order_number} - {customer.full_name} (VIP - مابقی)',
                reference_type='order',
                reference_id=order.id
            )
            db.session.add(transaction_b)
    else:
        # مشتری عادی: 20000 تومان به صندوق B و باقی به صندوق A
        amount_to_b = 20000
        amount_to_a = order.total_amount - amount_to_b
        if amount_to_a < 0:
            amount_to_b = order.total_amount
            amount_to_a = 0
        cashbox_b.balance += amount_to_b
        if amount_to_b > 0:
            transaction_b = CashBoxTransaction(
                cashbox_id=cashbox_b.id,
                amount=amount_to_b,
                transaction_type='income',
                description=f'درآمد سفارش {order.order_number} - {customer.full_name} (معمولی - سهم B)',
                reference_type='order',
                reference_id=order.id
            )
            db.session.add(transaction_b)
        if amount_to_a > 0:
            cashbox_a.balance += amount_to_a
            transaction_a = CashBoxTransaction(
                cashbox_id=cashbox_a.id,
                amount=amount_to_a,
                transaction_type='income',
                description=f'درآمد سفارش {order.order_number} - {customer.full_name} (معمولی - سهم A)',
                reference_type='order',
                reference_id=order.id
            )
            db.session.add(transaction_a)

def generate_order_number():
    """تولید شماره سفارش منحصر به فرد"""
    import random
    import string

    # تولید شماره تصادفی 6 رقمی
    while True:
        number = ''.join(random.choices(string.digits, k=6))
        order_number = f"ORD{number}"

        # بررسی تکراری نبودن
        if not Order.query.filter_by(order_number=order_number).first():
            return order_number

def update_cancelled_orders():
    """Update any cancelled orders to pending status"""
    cancelled_orders = Order.query.filter_by(status='cancelled').all()
    for order in cancelled_orders:
        order.status = 'pending'
    db.session.commit()

def generate_order_number():
    """تولید شماره سفارش ترتیبی ساده"""
    # دریافت آخرین سفارش
    last_order = Order.query.order_by(Order.id.desc()).first()

    if last_order:
        # اگر سفارش قبلی وجود دارد، شماره بعدی را تولید کن
        try:
            # اگر شماره قبلی عددی است، یکی اضافه کن
            last_number = int(last_order.order_number)
            next_number = last_number + 1
        except ValueError:
            # اگر شماره قبلی عددی نیست، از تعداد کل سفارشات استفاده کن
            total_orders = Order.query.count()
            next_number = total_orders + 1
    else:
        # اولین سفارش - شروع از 1
        next_number = 1

    # بررسی تکراری نبودن (احتیاط اضافی)
    while Order.query.filter_by(order_number=str(next_number)).first():
        next_number += 1

    return str(next_number)

@bp.route('/orders')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    date_filter = request.args.get('date_filter', '')
    
    query = Order.query
    
    if search:
        query = query.join(Customer).filter(
            or_(
                Order.order_number.ilike(f'%{search}%'),
                Customer.first_name.ilike(f'%{search}%'),
                Customer.last_name.ilike(f'%{search}%')
            )
        )
    
    if status:
        query = query.filter_by(status=status)
    
    # فیلتر تاریخ
    if date_filter:
        today = datetime.utcnow().date()
        if date_filter == 'today':
            query = query.filter(func.date(Order.created_at) == today)
        elif date_filter == 'yesterday':
            yesterday = today - timedelta(days=1)
            query = query.filter(func.date(Order.created_at) == yesterday)
        elif date_filter == 'this_week':
            start_of_week = today - timedelta(days=today.weekday())
            query = query.filter(func.date(Order.created_at) >= start_of_week)
        elif date_filter == 'last_week':
            start_of_week = today - timedelta(days=today.weekday())
            start_of_last_week = start_of_week - timedelta(days=7)
            end_of_last_week = start_of_week - timedelta(days=1)
            query = query.filter(
                func.date(Order.created_at) >= start_of_last_week,
                func.date(Order.created_at) <= end_of_last_week
            )
        elif date_filter == 'this_month':
            start_of_month = today.replace(day=1)
            query = query.filter(func.date(Order.created_at) >= start_of_month)
        elif date_filter == 'last_month':
            if today.month == 1:
                start_of_last_month = today.replace(year=today.year-1, month=12, day=1)
            else:
                start_of_last_month = today.replace(month=today.month-1, day=1)
            end_of_last_month = today.replace(day=1) - timedelta(days=1)
            query = query.filter(
                func.date(Order.created_at) >= start_of_last_month,
                func.date(Order.created_at) <= end_of_last_month
            )
    
    # مرتب‌سازی بر اساس ID (که با شماره سفارش ترتیبی همخوانی دارد)
    # آخرین سفارش (بالاترین ID/شماره) بالاتر نمایش داده می‌شود
    orders = query.order_by(Order.id.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    
    return render_template('orders/index.html', orders=orders, search=search, status=status, date_filter=date_filter)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """ایجاد سفارش جدید"""
    form = OrderForm()
    expense_form = OrderExpenseForm()
    form.customer_id.choices = [(c.id, c.full_name) for c in Customer.query.order_by(Customer.first_name).all()]
    if form.validate_on_submit():
        # محاسبه مبلغ کل
        total_amount = 0
        lens_type_ids = request.form.getlist('lens_type_id[]')
        lens_cut_type_ids = request.form.getlist('lens_cut_type_id[]')
        quantities = request.form.getlist('lens_quantity[]')
        prices = request.form.getlist('lens_price[]')
        if not lens_type_ids or not lens_cut_type_ids or not quantities or not prices:
            flash('لطفاً حداقل یک عدسی به سفارش اضافه کنید.', 'error')
            return render_template('orders/new.html',
                                form=form,
                                expense_form=expense_form,
                                title='سفارش جدید',
                                customers=Customer.query.order_by(Customer.first_name).all(),
                                lens_types=LensType.query.order_by(LensType.name).all(),
                                lens_cut_types=LensCutType.query.order_by(LensCutType.name).all(),
                                today_date=date.today().strftime('%Y-%m-%d'))
        for i in range(len(lens_type_ids)):
            if lens_type_ids[i] and lens_cut_type_ids[i] and quantities[i] and prices[i]:
                total_amount += float(prices[i])
        # هزینه اختیاری
        expense_title = request.form.get('title', '').strip()
        expense_amount = request.form.get('amount', '').strip()
        # حذف کامل تاریخ هزینه
        expense_description = request.form.get('description', '').strip()
        # اگر هیچ‌کدام از فیلدهای هزینه وارد نشده بود، هزینه را 0 قرار بده و هزینه ثبت نکن
        if not expense_title and not expense_amount:
            add_expense = False
            expense_amount = 0
        # اگر فقط یکی از فیلدها وارد شده بود یا مقدار نامعتبر بود، هزینه ثبت نکن و مقدار را 0 قرار بده
        elif not expense_title or not expense_amount or not expense_amount.replace('.', '', 1).isdigit() or float(expense_amount) <= 0:
            add_expense = False
            expense_amount = 0
        else:
            add_expense = True
            total_amount += float(expense_amount)  # هزینه به مبلغ سفارش اضافه می‌شود
        # ایجاد سفارش
        order = Order(
            order_number=generate_order_number(),
            customer_id=form.customer_id.data,
            created_at=datetime.strptime(request.form['created_at'], '%Y-%m-%d'),
            payment=form.payment.data or 0,
            notes=form.notes.data,
            total_amount=total_amount,
            status='in_progress'  # وضعیت پیش‌فرض: در حال انجام
        )
        db.session.add(order)
        db.session.flush()
        # اضافه کردن عدسی‌ها
        for i in range(len(lens_type_ids)):
            if lens_type_ids[i] and lens_cut_type_ids[i] and quantities[i] and prices[i]:
                order_lens = OrderLens(
                    order_id=order.id,
                    lens_type_id=lens_type_ids[i],
                    lens_cut_type_id=lens_cut_type_ids[i],
                    quantity=int(quantities[i]),
                    price=float(prices[i])
                )
                db.session.add(order_lens)
        # اگر هزینه وارد شده بود، فقط هزینه را ثبت کن و هیچ مبلغی از صندوق کم نکن و تراکنش نساز
        if add_expense:
            expense = Expense(
                title=expense_title,
                amount=float(expense_amount),
                description=expense_description,
                customer_id=form.customer_id.data
            )
            db.session.add(expense)
            db.session.flush()
        # توزیع درآمد به صندوق‌ها فقط بر اساس جمع عدسی‌ها (بدون هزینه)
        order_amount_with_expense = order.total_amount
        order.total_amount = sum(float(prices[i]) for i in range(len(lens_type_ids)) if lens_type_ids[i] and lens_cut_type_ids[i] and quantities[i] and prices[i])
        distribute_income_to_cashboxes(order)
        order.total_amount = order_amount_with_expense
        # اضافه کردن پیش‌پرداخت به صندوق اصلی
        if order.payment > 0:
            cashbox_main = CashBox.query.filter_by(name='اصلی').first()
            if not cashbox_main:
                cashbox_main = CashBox(name='اصلی', balance=0.0)
                db.session.add(cashbox_main)
                db.session.flush()
            cashbox_main.balance += order.payment
            transaction = CashBoxTransaction(
                cashbox_id=cashbox_main.id,
                amount=order.payment,
                transaction_type='income',
                description=f'پیش‌پرداخت سفارش {order.order_number} - {order.customer.full_name}',
                reference_type='prepayment',
                reference_id=order.id
            )
            db.session.add(transaction)
        db.session.commit()
        flash('سفارش با موفقیت ثبت شد.', 'success')
        return redirect(url_for('orders.index'))
    # دریافت لیست نوع عدسی‌ها و نوع تراش‌ها
    lens_types = LensType.query.order_by(LensType.name).all()
    lens_cut_types = LensCutType.query.order_by(LensCutType.name).all()
    from datetime import date
    return render_template('orders/new.html',
                         form=form,
                         expense_form=expense_form,
                         title='سفارش جدید',
                         customers=Customer.query.order_by(Customer.first_name).all(),
                         lens_types=lens_types,
                         lens_cut_types=lens_cut_types,
                         today_date=date.today().strftime('%Y-%m-%d'))

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """ویرایش سفارش"""
    order = Order.query.get_or_404(id)
    form = OrderForm(obj=order)
    form.customer_id.choices = [(c.id, c.full_name) for c in Customer.query.order_by(Customer.first_name).all()]
    
    if form.validate_on_submit():
        # حذف تراکنش‌های قبلی صندوق مرتبط با این سفارش
        transactions = CashBoxTransaction.query.filter_by(reference_type='order', reference_id=order.id).all()
        for t in transactions:
            if t.transaction_type == 'income':
                t.cashbox.balance -= t.amount
            elif t.transaction_type == 'expense':
                t.cashbox.balance += t.amount
            db.session.delete(t)
        
        # محاسبه مبلغ کل
        total_amount = 0
        lens_type_ids = request.form.getlist('lens_type_id[]')
        lens_cut_type_ids = request.form.getlist('lens_cut_type_id[]')
        quantities = request.form.getlist('lens_quantity[]')
        prices = request.form.getlist('lens_price[]')

        # بررسی وجود داده‌های عدسی
        if not lens_type_ids or not lens_cut_type_ids or not quantities or not prices:
            flash('لطفاً حداقل یک عدسی به سفارش اضافه کنید.', 'error')
            return render_template('orders/form.html',
                                form=form,
                                order=order,
                                title='ویرایش سفارش',
                                customers=Customer.query.order_by(Customer.first_name).all(),
                                lens_types=LensType.query.order_by(LensType.name).all(),
                                lens_cut_types=LensCutType.query.order_by(LensCutType.name).all())
        
        # محاسبه مبلغ کل
        for i in range(len(lens_type_ids)):
            if lens_type_ids[i] and lens_cut_type_ids[i] and quantities[i] and prices[i]:
                total_amount += float(prices[i])
        
        # ذخیره مقدار قبلی پیش‌پرداخت برای محاسبه تفاوت
        old_payment = order.payment or 0
        new_payment = form.payment.data or 0
        payment_difference = new_payment - old_payment

        # به‌روزرسانی سفارش
        order.customer_id = form.customer_id.data
        order.created_at = datetime.strptime(request.form['created_at'], '%Y-%m-%d')
        order.payment = new_payment
        order.notes = form.notes.data
        order.total_amount = total_amount
        
        # حذف عدسی‌های قبلی
        OrderLens.query.filter_by(order_id=order.id).delete()
        
        # اضافه کردن عدسی‌های جدید
        for i in range(len(lens_type_ids)):
            if lens_type_ids[i] and lens_cut_type_ids[i] and quantities[i] and prices[i]:
                order_lens = OrderLens(
                    order_id=order.id,
                    lens_type_id=lens_type_ids[i],
                    lens_cut_type_id=lens_cut_type_ids[i],
                    quantity=int(quantities[i]),
                    price=float(prices[i])
                )
                db.session.add(order_lens)

        # اعمال تفاوت پیش‌پرداخت در صندوق اصلی
        if payment_difference != 0:
            cashbox_main = CashBox.query.filter_by(name='اصلی').first()
            if not cashbox_main:
                cashbox_main = CashBox(name='اصلی', balance=0.0)
                db.session.add(cashbox_main)
                db.session.flush()

            # اعمال تفاوت در صندوق اصلی
            cashbox_main.balance += payment_difference

            # ثبت تراکنش تصحیح پیش‌پرداخت
            transaction = CashBoxTransaction(
                cashbox_id=cashbox_main.id,
                amount=abs(payment_difference),
                transaction_type='income' if payment_difference > 0 else 'expense',
                description=f'تصحیح پیش‌پرداخت سفارش {order.order_number} - {order.customer.full_name}',
                reference_type='prepayment_adjustment',
                reference_id=order.id
            )
            db.session.add(transaction)

        # پس از ذخیره سفارش جدید، توزیع درآمد جدید به صندوق‌ها
        db.session.flush()
        distribute_income_to_cashboxes(order)
        db.session.commit()
        flash('سفارش با موفقیت به‌روزرسانی شد و تغییرات در صندوق لحاظ شد.', 'success')
        return redirect(url_for('orders.show', id=order.id))
    
    # دریافت لیست نوع عدسی‌ها و نوع تراش‌ها
    lens_types = LensType.query.order_by(LensType.name).all()
    lens_cut_types = LensCutType.query.order_by(LensCutType.name).all()
    
    return render_template('orders/form.html', 
                         form=form, 
                         order=order,
                         title='ویرایش سفارش',
                         customers=Customer.query.order_by(Customer.first_name).all(),
                         lens_types=lens_types,
                         lens_cut_types=lens_cut_types)

@bp.route('/orders/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    order = Order.query.get_or_404(id)
    # حذف تراکنش‌های صندوق مرتبط با این سفارش
    transactions = CashBoxTransaction.query.filter_by(reference_type='order', reference_id=order.id).all()
    for t in transactions:
        # بازگرداندن مبلغ تراکنش به صندوق مربوطه (برعکس نوع تراکنش)
        if t.transaction_type == 'income':
            t.cashbox.balance -= t.amount
        elif t.transaction_type == 'expense':
            t.cashbox.balance += t.amount
        db.session.delete(t)
    db.session.delete(order)
    db.session.commit()
    flash('سفارش با موفقیت حذف شد و تغییرات در صندوق لحاظ شد.', 'success')
    return redirect(url_for('orders.index'))

@bp.route('/orders/<int:id>/status', methods=['POST'])
@login_required
def update_status(id):
    """به‌روزرسانی وضعیت سفارش"""
    try:
        # دریافت سفارش
        order = Order.query.get_or_404(id)
        # دریافت وضعیت جدید
        new_status = request.form.get('status')

        # بررسی معتبر بودن وضعیت
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'وضعیت نامعتبر است.'}), 400
            flash('وضعیت نامعتبر است.', 'error')
            return redirect(url_for('orders.index'))

        # به‌روزرسانی وضعیت
        order.status = new_status
        db.session.commit()

        # پیام موفقیت
        status_names = {
            'pending': 'در انتظار',
            'in_progress': 'در حال انجام',
            'completed': 'تکمیل شده',
            'cancelled': 'لغو شده'
        }

        # اگر درخواست AJAX باشد، JSON برگردان
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': f'وضعیت سفارش به "{status_names.get(new_status, new_status)}" تغییر یافت.',
                'new_status': new_status,
                'status_display': status_names.get(new_status, new_status)
            })

        # اگر درخواست معمولی باشد، redirect کن
        flash(f'وضعیت سفارش به "{status_names.get(new_status, new_status)}" تغییر یافت.', 'success')
        return redirect(url_for('orders.index'))

    except Exception as e:
        db.session.rollback()
        error_message = f'خطا در به‌روزرسانی وضعیت سفارش: {str(e)}'

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': error_message}), 500

        flash(error_message, 'error')
        return redirect(url_for('orders.index'))

@bp.route('/orders/<int:id>')
@login_required
def show(id):
    order = Order.query.get_or_404(id)
    return render_template('orders/show.html', order=order)

@bp.route('/orders/<int:id>/settle', methods=['POST'])
@login_required
def settle_order(id):
    """تسویه سفارش"""
    order = Order.query.get_or_404(id)

    try:
        paid_amount = float(request.form.get('paid_amount', 0))
        settlement_notes = request.form.get('settlement_notes', '').strip()

        if paid_amount <= 0:
            return jsonify({'success': False, 'message': 'مبلغ پرداختی باید بیشتر از صفر باشد'})

        if paid_amount > order.remaining_amount:
            return jsonify({'success': False, 'message': 'مبلغ پرداختی نمی‌تواند بیشتر از مانده باشد'})

        # بروزرسانی مبلغ پرداخت شده
        current_paid = order.paid_amount or 0.0
        order.paid_amount = current_paid + paid_amount

        # بررسی تسویه کامل
        if order.total_paid_amount >= order.total_amount:
            order.is_settled = True
            order.settlement_date = datetime.now()

        # اضافه کردن یادداشت
        if settlement_notes:
            if order.settlement_notes:
                order.settlement_notes += f"\n{datetime.now().strftime('%Y/%m/%d %H:%M')}: {settlement_notes}"
            else:
                order.settlement_notes = f"{datetime.now().strftime('%Y/%m/%d %H:%M')}: {settlement_notes}"

        order.updated_at = datetime.now()

        # اضافه کردن مبلغ پرداختی به صندوق اصلی
        cashbox_main = CashBox.query.filter_by(name='اصلی').first()
        if not cashbox_main:
            cashbox_main = CashBox(name='اصلی', balance=0.0)
            db.session.add(cashbox_main)
            db.session.flush()

        # اضافه کردن مبلغ به صندوق اصلی
        cashbox_main.balance += paid_amount

        # ثبت تراکنش در صندوق اصلی
        transaction = CashBoxTransaction(
            cashbox_id=cashbox_main.id,
            amount=paid_amount,
            transaction_type='income',
            description=f'تسویه سفارش {order.order_number} - {order.customer.full_name}',
            reference_type='settlement',
            reference_id=order.id
        )
        db.session.add(transaction)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'تسویه با موفقیت ثبت شد',
            'paid_amount': order.paid_amount,
            'total_paid_amount': order.total_paid_amount,
            'remaining_amount': order.remaining_amount,
            'is_settled': order.is_settled,
            'settlement_status': order.settlement_status_display
        })

    except ValueError:
        return jsonify({'success': False, 'message': 'مبلغ وارد شده نامعتبر است'})
    except Exception as e:
        db.session.rollback()
        print(f"Error in settle_order: {str(e)}")  # برای دیباگ
        return jsonify({'success': False, 'message': f'خطا در ثبت تسویه: {str(e)}'})

@bp.route('/orders/<int:id>/settlement-history')
@login_required
def settlement_history(id):
    """تاریخچه تسویه سفارش"""
    order = Order.query.get_or_404(id)
    return jsonify({
        'order_number': order.order_number,
        'customer_name': order.customer.full_name,
        'total_amount': order.total_amount,
        'prepayment': order.payment or 0.0,
        'paid_amount': order.paid_amount or 0.0,
        'total_paid_amount': order.total_paid_amount,
        'remaining_amount': order.remaining_amount,
        'is_settled': order.is_settled,
        'settlement_date': order.settlement_date.strftime('%Y/%m/%d %H:%M') if order.settlement_date else None,
        'settlement_notes': order.settlement_notes or ''
    })

@bp.route('/orders/<int:order_id>/add-expense', methods=['POST'])
@login_required
def add_order_expense(order_id):
    order = Order.query.get_or_404(order_id)
    form = OrderExpenseForm()
    if form.validate_on_submit():
        title = form.title.data.strip()
        amount = form.amount.data
        description = form.description.data.strip()
        # ثبت هزینه مرتبط با سفارش و مشتری
        expense = Expense(
            title=title,
            amount=amount,
            description=description,
            customer_id=order.customer_id
        )
        db.session.add(expense)
        db.session.flush()
        # انتخاب صندوق بر اساس نوع مشتری
        customer = order.customer
        if customer and customer.is_vip:
            cashbox = CashBox.query.filter_by(name='B').first()
            if not cashbox:
                cashbox = CashBox(name='B', balance=0.0)
                db.session.add(cashbox)
                db.session.flush()
        else:
            cashbox = CashBox.query.filter_by(name='A').first()
            if not cashbox:
                cashbox = CashBox(name='A', balance=0.0)
                db.session.add(cashbox)
                db.session.flush()
        cashbox.balance -= amount
        transaction = CashBoxTransaction(
            cashbox_id=cashbox.id,
            amount=amount,
            transaction_type='expense',
            description=f'هزینه سفارش: {title}',
            reference_type='order_expense',
            reference_id=expense.id
        )
        db.session.add(transaction)
        # دیگر مبلغ کل سفارش افزایش نمی‌یابد چون هزینه نباید در total_amount لحاظ شود
        db.session.commit()
        flash('هزینه به فاکتور اضافه شد و مبلغ کل به‌روزرسانی شد.', 'success')
    else:
        flash('خطا در ثبت هزینه. لطفاً اطلاعات را کامل وارد کنید.', 'error')
    return redirect(url_for('orders.show', id=order_id))