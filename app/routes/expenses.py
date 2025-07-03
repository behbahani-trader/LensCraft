from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.expense import Expense
from app.models.cashbox import CashBox, CashBoxTransaction
from app import db
from datetime import datetime
from app.forms.expense import ExpenseForm
from app.models.customer import Customer

bp = Blueprint('expenses', __name__)

@bp.route('/expenses')
@login_required
def index():
    """لیست هزینه‌ها"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Expense.query
    if search:
        query = query.filter(Expense.title.ilike(f'%{search}%'))
    
    expenses = query.order_by(Expense.expense_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # محاسبه مجموع هزینه‌ها
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    
    return render_template('expenses/index.html', 
                         expenses=expenses, 
                         search=search,
                         total_expenses=total_expenses)

@bp.route('/expenses/new', methods=['GET', 'POST'])
@login_required
def new():
    """ثبت هزینه جدید"""
    form = ExpenseForm()
    form.customer_id.choices = [(c.id, c.full_name) for c in Customer.query.order_by(Customer.first_name).all()]
    if form.validate_on_submit():
        title = form.title.data.strip()
        amount = form.amount.data
        description = form.description.data.strip()
        expense_date = form.expense_date.data or datetime.now()
        customer_id = form.customer_id.data
        customer = Customer.query.get(customer_id)
        # ثبت هزینه
        expense = Expense(
            title=title,
            amount=amount,
            description=description,
            expense_date=expense_date,
            customer_id=customer_id
        )
        db.session.add(expense)
        db.session.flush()
        # انتخاب صندوق بر اساس نوع مشتری
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
            description=f'هزینه: {title}',
            reference_type='expense',
            reference_id=expense.id
        )
        db.session.add(transaction)
        db.session.commit()
        flash('هزینه با موفقیت ثبت شد و از صندوق مناسب کسر گردید.', 'success')
        return redirect(url_for('expenses.index'))
    return render_template('expenses/new.html', form=form)

@bp.route('/expenses/<int:id>')
@login_required
def show(id):
    """نمایش جزئیات هزینه"""
    expense = Expense.query.get_or_404(id)
    return render_template('expenses/show.html', expense=expense)

@bp.route('/expenses/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """ویرایش هزینه"""
    expense = Expense.query.get_or_404(id)
    old_amount = expense.amount
    form = ExpenseForm(obj=expense)
    form.customer_id.choices = [(c.id, c.full_name) for c in Customer.query.order_by(Customer.first_name).all()]
    if form.validate_on_submit():
        title = form.title.data.strip()
        amount = form.amount.data
        description = form.description.data.strip()
        expense_date = form.expense_date.data or expense.expense_date
        customer_id = form.customer_id.data
        customer = Customer.query.get(customer_id)
        # بروزرسانی هزینه
        expense.title = title
        expense.amount = amount
        expense.description = description
        expense.expense_date = expense_date
        expense.customer_id = customer_id
        expense.updated_at = datetime.now()
        # تصحیح موجودی صندوق مناسب
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
        # برگرداندن مبلغ قبلی و کسر مبلغ جدید
        cashbox.balance += old_amount - amount
        if old_amount != amount:
            transaction = CashBoxTransaction(
                cashbox_id=cashbox.id,
                amount=abs(old_amount - amount),
                transaction_type='income' if old_amount > amount else 'expense',
                description=f'تصحیح هزینه: {title}',
                reference_type='expense',
                reference_id=expense.id
            )
            db.session.add(transaction)
        db.session.commit()
        flash('هزینه با موفقیت بروزرسانی شد.', 'success')
        return redirect(url_for('expenses.index'))
    return render_template('expenses/edit.html', expense=expense, form=form)

@bp.route('/expenses/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """حذف هزینه"""
    expense = Expense.query.get_or_404(id)
    
    try:
        customer = Customer.query.get(expense.customer_id)
        # برگرداندن مبلغ به صندوق مناسب
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
        cashbox.balance += expense.amount
        # ثبت تراکنش برگشت
        transaction = CashBoxTransaction(
            cashbox_id=cashbox.id,
            amount=expense.amount,
            transaction_type='income',
            description=f'حذف هزینه: {expense.title}',
            reference_type='expense',
            reference_id=expense.id
        )
        db.session.add(transaction)
        # حذف تراکنش‌های مرتبط
        CashBoxTransaction.query.filter_by(
            reference_type='expense',
            reference_id=expense.id
        ).delete()
        db.session.delete(expense)
        db.session.commit()
        flash('هزینه با موفقیت حذف شد و مبلغ به صندوق مناسب برگردانده شد.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('خطا در حذف هزینه. لطفاً دوباره تلاش کنید.', 'error')
    
    return redirect(url_for('expenses.index'))
