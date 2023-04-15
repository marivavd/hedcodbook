from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    name = StringField('Название книги', validators=[DataRequired()])
    author = StringField('Имя и фамилия автора', validators=[DataRequired()])
    picture = StringField('Обложка книги', validators=[DataRequired()])
    genre = StringField('Жанр', validators=[DataRequired()])
    summary = TextAreaField('Краткое содержание', validators=[DataRequired()])
    history_of_creation = TextAreaField('История создания', validators=[DataRequired()])
    link_to_the_book = StringField('Ссылка на произведение', validators=[DataRequired()])
    link_to_the_production = StringField('Ссылка на постановку в театре', validators=[DataRequired()])
    link_to_audio = StringField('Ссылка на аудиокнигу', validators=[DataRequired()])
    link_to_the_screenshot = StringField('Ссылка на фильм', validators=[DataRequired()])
    submit = SubmitField('Добавить')