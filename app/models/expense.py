from datetime import datetime
from app import db
from app.models.customer import Customer

class Expense(db.Model):
    """مدل برای هزینه‌ها"""
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))  # مشتری مرتبط با هزینه
    customer = db.relationship('Customer')
    
    def __repr__(self):
        return f'<Expense {self.title}: {self.amount}>'
