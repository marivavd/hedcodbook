"""Модуль для переключения между страницами"""
from flask import Flask, render_template, redirect, request, abort, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.user import RegisterForm, LoginForm
from forms.book import PostForm
from data.users import User
from data.library import Library
from data.authors import Authors
from data import db_session, main_api

from requests import get
import random

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
            nickname=form.nickname.data,
            avatar=random.choice(['avatar_raccoon.jpg', 'avatar_hedgehog.jpg'])
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


@app.route("/", methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
        return render_template('index.html')

    return render_template("home.html", sp_books=get(f'http://127.0.0.1:8000/api/index/'
                                                     f'{request.form.get("book_filter")}_/'
                                                     f'{request.form.get("search")}_').json())


@app.route("/user_page")
def user_page():
    if current_user.is_authenticated:
        sp_reading_now = current_user.books['reading_now']
        sp_want_to_read = current_user.books["want_to_read"]
        sp_were_read = current_user.books['were_read']
        sp_all = []
        for i in range(max(len(sp_want_to_read), len(sp_were_read), len(sp_reading_now))):
            if len(sp_want_to_read) < i + 1:
                sp_all.append(['', '/user_page'])
            else:
                sp_all.append([sp_want_to_read[i].name, f'/book/{sp_want_to_read[i].id}'])
            if len(sp_reading_now) < i + 1:
                sp_all.append(['', '/user_page'])
            else:
                sp_all.append([sp_reading_now[i].name, f'/book/{sp_reading_now[i].id}'])
            if len(sp_were_read) < i + 1:
                sp_all.append(['', '/user_page'])
            else:
                sp_all.append([sp_were_read[i].name, f'/book/{sp_were_read[i].id}'])
        return render_template("user_page.html", len_sp=len(sp_all), sp_all=sp_all)


@app.route("/add_book")
def add_book():
    form = PostForm()
    db_sess = db_session.create_session()
    sp_authors = db_sess.query(Authors).all()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        check_book = db_sess.query(Library).filter(Library.name.lower() == form.name.data.lower()).first()
        if check_book:  # проверка на нахождение книги в библиотеке
            return render_template('add_book.html', message="Эта книга уже есть в нашей библиотеке", form=form,
                                   sp_authors=sp_authors)
        if form.name.data.lower() == 'я':
            add_author(current_user.name, current_user.surname)
        elif form.name.data.lower() == 'другое':
            add_author()
        # прописать POST запрос
    return render_template("add_book.html", sp_authors=sp_authors, form=form)


@app.route("/add_author")
def add_author(name='', surname=''):
    pass


@app.route("/book/<int:book_id>")
def open_book(book_id):
    db_sess = db_session.create_session()
    book = db_sess.query(Library).filter(Library.id == book_id).first()
    sl_reviews = book.reviews
    stars = book.summa_marks // book.count_marks
    author = db_sess.query(Authors).filter(Authors.id == book.author_id).first()
    return render_template("book.html", book=book, author=author, sl_reviews=sl_reviews, stars=stars)


@app.route("/author/<int:author_id>")
def open_author(author_id):
    db_sess = db_session.create_session()
    author = db_sess.query(Authors).filter(Authors.id == author_id).first()
    sp_books = db_sess.query(Library).filter(Library.author_id == author_id).all()
    return render_template("author.html", author=author, sp_books=sp_books)


@app.route("/no_information")
def no_information():
    return render_template("no_information.html")


@app.route("/authors")
def open_page_with_authors():
    db_sess = db_session.create_session()
    authors = db_sess.query(Authors).all()
    return render_template("authors.html", authors=authors, n=len(authors))


if __name__ == '__main__':
    db_session.global_init("db/library.db")
    app.register_blueprint(main_api.blueprint)
    app.run(port=8000)
