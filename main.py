"""Модуль для переключения между страницами"""
from flask import Flask, render_template, redirect, request, abort, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from forms.user import RegisterForm, LoginForm
from forms.book import PostForm
from forms.author import AuthorForm

from data.users import User
from data.library import Library
from data.authors import Authors
from data.db import MyDataBase

from api import main_api
from requests import get, put, post
from data import db_session

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db = MyDataBase()


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
def register():
    form = RegisterForm()

    if not form.validate_on_submit():
        return render_template('register.html', title='Регистрация', form=form)

    db_sess = db_session.create_session()
    if not form.check_password_again():
        return render_template('register.html', title='Регистрация', form=form,
                               message="Пароли не совпадают")
    elif db_sess.query(User).filter(User.email == form.email.data).first():
        return render_template('register.html', title='Регистрация', form=form,
                               message="Такой пользователь уже есть")
    else:
        get('http://127.0.0.1:5000/api/register/', params=form.get_public())
        return redirect('/login')


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

    return render_template("home.html", sp_books=get(f'http://127.0.0.1:5000/api/index/'
                                                     f'{request.form.get("book_filter")}_/'
                                                     f'{request.form.get("search")}_').json())


@app.route("/user_page")
def user_page():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        sp_reading_now = current_user.books['reading_now']
        sp_want_to_read = current_user.books["want_to_read"]
        sp_were_read = current_user.books['were_read']
        sp_all = []
        for i in range(max(len(sp_want_to_read), len(sp_were_read), len(sp_reading_now))):
            if len(sp_want_to_read) < i + 1:
                sp_all.append(['', '/user_page'])
            else:
                book = db_sess.query(Library).filter(Library.id == sp_want_to_read[i]).first()
                sp_all.append([book.name, f'/book/{sp_want_to_read[i]}'])
            if len(sp_reading_now) < i + 1:
                sp_all.append(['', '/user_page'])
            else:
                book = db_sess.query(Library).filter(Library.id == sp_reading_now[i]).first()
                sp_all.append([book.name, f'/book/{sp_reading_now[i]}'])
            if len(sp_were_read) < i + 1:
                sp_all.append(['', '/user_page'])
            else:
                book = db_sess.query(Library).filter(Library.id == sp_were_read[i]).first()
                sp_all.append([book.name, f'/book/{sp_were_read[i]}'])
        return render_template("user_page.html", len_sp=len(sp_all), sp_all=sp_all)


@app.route("/add_author", methods=['GET', 'POST'])
def add_author():
    form = AuthorForm()

    if request.method == 'GET':
        return render_template('add_author.html', form=form)

    if not form.validate_on_submit():
        return render_template("add_author.html", form=form)

    if db.get_author(*form.get_fullname()):
        return render_template('add_author.html', message="Этот автор уже с нами", form=form)

    f = request.files['picture']
    photo_file = open(f'static/img/authors/{"_".join(form.get_fullname())}.png', "wb")
    photo_file.write(f.read())

    put('http://127.0.0.1:5000/api/add_author', params=form.get_all())
    return redirect('/')


@app.route("/add_book", methods=['POST', 'GET'])
def add_book():
    form = PostForm()

    if not form.validate_on_submit() or request.method == 'GET':
        return render_template("add_book.html", sp_authors=db.get_sp_authors(), form=form)
    form += request.form.get('comp_select')

    if db.check_book(form.name.data):
        return render_template('add_book.html',
                               message="Эта книга уже есть в нашей библиотеке",
                               form=form, sp_authors=db.get_sp_authors())

    is_new_author = get('http://127.0.0.1:5000/api/add_book/',
                        params=form.get_all()).json()['is_new_author']

    f = request.files['picture']
    photo_file = open(f'static/img/books/{form.name.data.lower()}.jpg', "wb")
    photo_file.write(f.read())

    if is_new_author:
        return redirect('/add_author')
    else:
        return redirect('/')


@app.route("/book/<int:book_id>", methods=['GET', 'POST'])
def open_book(book_id):
    if request.method == "POST":
        status = request.form['status']
        for i in ["reading_now", "want_to_read", "were_read"]:
            if i == status and book_id not in current_user.books[i]:
                current_user.books[status].append(book_id)
            elif i != status and book_id in current_user.books[i]:
                current_user.books[i].remove(book_id)
        put(f'http://127.0.0.1:5000/api/edit_status/{current_user.id}',
            json={'books': current_user.books, 'id': current_user.id}).json()
    db_sess = db_session.create_session()
    book = db_sess.query(Library).filter(Library.id == book_id).first()
    sl_reviews = book.reviews
    if book.count_marks == 0:
        stars = 0
    else:
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


@app.route("/reviews/<int:user_id>")
def reviews(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    sl_reviews = user.books["comments"]
    sl_names_books = {}

    for key, val in sl_reviews.items():
        sl_names_books[key] = db_sess.query(Library).filter(Library.id == key).first().name
    return render_template("reviews.html", sl_reviews=sl_reviews, books=sl_names_books)


@app.route("/marks/<int:user_id>")
def marks(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    sl_marks = user.books["marks"]
    sl_names_books = {}
    for key, val in sl_marks.items():
        sl_names_books[key] = db_sess.query(Library).filter(Library.id == key).first().name
    return render_template("marks.html", sl_marks=sl_marks, books=sl_names_books)


@app.route("/send_marks/<int:book_id>", methods=['GET', 'POST'])
def send_marks(book_id):
    if request.method == 'POST':
        mark = request.form['mark']
        current_user.books['marks'][book_id] = int(mark)
        put(f'http://127.0.0.1:5000/api/comment_mark/{current_user.id}',
            json={'books': current_user.books, 'id': current_user.id}).json()
        db_sess = db_session.create_session()
        book = db_sess.query(Library).filter(Library.id == book_id).first()
        book.summa_marks += int(mark)
        book.count_marks += 1
        db_sess.commit()
    return redirect(f'/book/{book_id}')


@app.route("/send_reviews/<int:book_id>", methods=['GET', 'POST'])
def send_reviews(book_id):
    if request.method == 'POST':
        message = request.form['user_message']
        current_user.books['comments'][int(book_id)] = message
        put(f'http://127.0.0.1:5000/api/comment_mark/{current_user.id}',
            json={'books': current_user.books, 'id': current_user.id}).json()
        db_sess = db_session.create_session()
        book = db_sess.query(Library).filter(Library.id == book_id).first()
        book.reviews[current_user.nickname] = message
        put(f'http://127.0.0.1:5000/api/comment_for_book/{book.id}',
            json={'reviews': book.reviews, 'id': book.id}).json()
    return redirect(f'/book/{book_id}')


if __name__ == '__main__':
    db_session.global_init("db/library.db")
    app.register_blueprint(main_api.blueprint)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
