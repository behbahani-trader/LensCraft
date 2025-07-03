from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, NumberRange

class ExpenseForm(FlaskForm):
    title = StringField('عنوان', validators=[DataRequired()])
    amount = FloatField('مبلغ', validators=[DataRequired(), NumberRange(min=1)])
    description = TextAreaField('توضیحات')
    expense_date = DateField('تاریخ هزینه', format='%Y-%m-%d')
    customer_id = SelectField('مشتری', coerce=int, validators=[DataRequired()])
