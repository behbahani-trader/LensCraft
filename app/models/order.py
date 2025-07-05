from datetime import datetime
from app import db
from app.utils.date_utils import format_jalali

class Order(db.Model):
    """مدل برای ذخیره سفارش‌ها"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment = db.Column(db.Float, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default='pending')
    notes = db.Column(db.Text)

    # فیلدهای تسویه
    paid_amount = db.Column(db.Float, default=0.0)  # مبلغ پرداخت شده
    is_settled = db.Column(db.Boolean, default=False)  # آیا تسویه شده؟
    settlement_date = db.Column(db.DateTime)  # تاریخ تسویه
    settlement_notes = db.Column(db.Text)  # یادداشت تسویه

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Relationships
    customer = db.relationship('Customer', back_populates='orders')
    lenses = db.relationship('OrderLens', back_populates='order', cascade='all, delete-orphan')
    expenses = db.relationship('Expense', back_populates='order', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

    @property
    def status_display(self):
        status_map = {
            'pending': 'در انتظار',
            'in_progress': 'در حال انجام',
            'completed': 'تکمیل شده',
            'cancelled': 'لغو شده'
        }
        return status_map.get(self.status, self.status)

    @property
    def status_color(self):
        color_map = {
            'pending': 'warning',  # زرد
            'in_progress': 'info',  # آبی
            'completed': 'success',  # سبز
            'cancelled': 'error'  # قرمز
        }
        return color_map.get(self.status, 'ghost')

    @property
    def next_status(self):
        status_flow = {
            'pending': 'in_progress',
            'in_progress': 'completed',
            'completed': 'completed',
            'cancelled': 'pending'
        }
        return status_flow.get(self.status, 'pending')

    @property
    def next_status_color(self):
        color_map = {
            'pending': 'warning',
            'in_progress': 'info',
            'completed': 'success',
            'cancelled': 'error'
        }
        return color_map.get(self.next_status, 'ghost')

    @property
    def lens_count(self):
        return sum(order_lens.quantity for order_lens in self.lenses)

    @property
    def jalali_created_at(self):
        return format_jalali(self.created_at)

    @property
    def jalali_delivery_date(self):
        return format_jalali(self.delivery_date)

    @property
    def expenses_total(self):
        """جمع کل هزینه‌های اضافی"""
        return sum(expense.amount for expense in self.expenses)

    @property
    def lenses_total(self):
        """جمع کل عدسی‌ها"""
        return sum(lens.price for lens in self.lenses)

    @property
    def total_paid_amount(self):
        """کل مبلغ پرداخت شده (پیش‌پرداخت + تسویه‌ها)"""
        prepayment = self.payment or 0.0
        settlement_payments = self.paid_amount or 0.0
        return prepayment + settlement_payments

    @property
    def remaining_amount(self):
        """مبلغ باقی‌مانده برای پرداخت"""
        return self.total_amount - self.total_paid_amount

    @property
    def settlement_status_display(self):
        """نمایش وضعیت تسویه"""
        if self.remaining_amount <= 0:
            return 'تسویه شده'
        elif self.total_paid_amount > 0:
            return 'تسویه جزئی'
        else:
            return 'تسویه نشده'

    @property
    def settlement_status_color(self):
        """رنگ وضعیت تسویه"""
        if self.remaining_amount <= 0:
            return 'success'
        elif self.total_paid_amount > 0:
            return 'warning'
        else:
            return 'error'