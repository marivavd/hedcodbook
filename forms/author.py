from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class AuthorForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    picture = StringField('Фото', validators=[DataRequired()])
    about = TextAreaField('Немного об авторе', validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def get_all(self):
        return {'name': self.name.data,
                'surname': self.surname.data,
                'picture': f'/static/img/authors/{"_".join(self.get_fullname())}.png',
                'about': self.about.data}

    def get_fullname(self):
        return self.name.data, self.surname.data
