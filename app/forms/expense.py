from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SelectField
from wtforms.validators import DataRequired, NumberRange

class ExpenseForm(FlaskForm):
    title = StringField('عنوان', validators=[DataRequired()])
    amount = FloatField('مبلغ', validators=[DataRequired(), NumberRange(min=1)])
    description = TextAreaField('توضیحات')
    customer_id = SelectField('مشتری', coerce=int, validators=[DataRequired()])
