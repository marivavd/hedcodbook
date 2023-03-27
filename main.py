from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.user import RegisterForm, LoginForm
from data.users import User
from data.library import Library
from data.authors import Authors
from data import db_session

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/library.db")
    app.run()


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            nickname=form.nickname.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.nickname == form.nickname.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/")
def index():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        books = db_sess.query(Library).filter(Library.count_marks != 0).all()
        books.sort(key=lambda i: (i.count_marks != 0, i.summa_marks / i.count_marks))
        return render_template("home.html", sp_books=books)
    else:
        return render_template('index.html')


@app.route("/user_page")
def user_page():
    if current_user.is_authenticated:
        return render_template("user_page.html", nickname=current_user.nickname)

@app.route("/add_book")
def add_book():
    return render_template("add_book.html")

@app.route("/for_you")
def for_you():
    return render_template("for_you.html")


@app.route("/book/<int:id>")
def book(id):
    ...

if __name__ == '__main__':
    main()
