from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField

class OrderExpenseForm(FlaskForm):
    title = StringField('عنوان')
    amount = FloatField('مبلغ')
    description = TextAreaField('توضیحات')
