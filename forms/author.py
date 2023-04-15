from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class AuthorForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    picture = StringField('Фото', validators=[DataRequired()])
    about = TextAreaField('Немного об авторе', validators=[DataRequired()])
    submit = SubmitField('Добавить')