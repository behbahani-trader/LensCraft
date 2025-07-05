from datetime import datetime
from app import db

class OrderLens(db.Model):
    """مدل برای ذخیره اطلاعات عدسی‌های هر سفارش"""
    __tablename__ = 'order_lenses'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    lens_type_id = db.Column(db.Integer, db.ForeignKey('lens_types.id'), nullable=False)
    lens_cut_type_id = db.Column(db.Integer, db.ForeignKey('lens_cut_types.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    order = db.relationship('Order', back_populates='lenses')
    lens_type = db.relationship('LensType', back_populates='order_lenses')
    lens_cut_type = db.relationship('LensCutType', back_populates='order_lenses')

    @property
    def unit_price(self):
        """محاسبه قیمت واحد"""
        if self.quantity > 0:
            return self.price / self.quantity
        return 0

    def __repr__(self):
        return f'<OrderLens {self.id}>'