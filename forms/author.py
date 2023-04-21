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
        return {'name': self.name.data.lower(),
                'surname': self.surname.data.lower(),
                'picture': self.picture.data,
                'about': self.about.data}

    def get_fullname(self):
        return self.name.data.lower(), self.surname.data.lower()
