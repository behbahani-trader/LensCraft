from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, DateField
from wtforms.validators import DataRequired, NumberRange

class OrderExpenseForm(FlaskForm):
    title = StringField('عنوان', validators=[DataRequired()])
    amount = FloatField('مبلغ', validators=[DataRequired(), NumberRange(min=1)])
    description = TextAreaField('توضیحات')
    expense_date = DateField('تاریخ هزینه', format='%Y-%m-%d')
