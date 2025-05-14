from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange


class DepartmentForm(FlaskForm):
    title = StringField('Название департамента', validators=[DataRequired()])
    chief_id = IntegerField('ID руководителя',
                          validators=[DataRequired(), NumberRange(min=1)])
    members = TextAreaField('ID участников (через запятую)',
                          validators=[DataRequired()])
    email = StringField('Email',
                        validators=[Email()])
    submit = SubmitField('Сохранить')