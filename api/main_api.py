from flask import request, jsonify, Blueprint

from data import db_session
from data.library import Library
from data.users import User
from data.authors import Authors
from data.db import MyDataBase

from random import choice
import json

blueprint = Blueprint('main_api', __name__, template_folder='templates')
db = MyDataBase()


@blueprint.route('/api/books', methods=['POST'])
def create_book():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    # дописать API
    return jsonify({'success': 'OK'})


def try_filter(old_f):
    def new_f(books, book_filter, search):
        try:
            return old_f(books, book_filter, search)
        except KeyError:
            print('ПП... какой неожиданный аргумент в main.api, нужно добавить ещё проверок в функцию filter_book')

    return new_f


@try_filter
def filter_book(books, book_filter, search):
    sl_filter = {'title': lambda x: search in str(x.name),
                 'name': lambda x: search in str(x.authors.name),
                 'surname': lambda x: search in str(x.authors.surname),
                 'genre': lambda x: search in str(x.genre)}
    return list(filter(sl_filter[book_filter], books))


@blueprint.route('/api/index/<book_filter>/<search>', methods=['GET'])
def index(book_filter, search):
    db_sess = db_session.create_session()
    books = db_sess.query(Library).filter(Library.count_marks != 0).all()

    book_filter, search = book_filter.strip('_'), search.strip('_')  # _ добавляется для работы API при ''
    if search not in (None, 'None'):
        books = filter_book(books, book_filter, search)

    books.sort(key=lambda i: (-i.summa_marks / i.count_marks, -i.count_marks))
    return json.dumps(books, default=lambda x: x.get_json_dict())


@blueprint.route('/api/register/', methods=['GET'])
def register():
    user = User(
        name=request.args.get('name'),
        surname=request.args.get('surname'),
        email=request.args.get('email'),
        nickname=request.args.get('nickname'),
        avatar=choice(['avatar_raccoon.jpg', 'avatar_hedgehog.jpg'])
    )
    user.set_password(request.args.get('password'))
    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()


@blueprint.route('/api/comment_mark/<user_id>', methods=['PUT'])
def comment_mark(user_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    user.books = request.json["books"]
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/comment_for_book/<book_id>', methods=['PUT'])
def comment_for_book(book_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    db_sess = db_session.create_session()
    book = db_sess.query(Library).get(book_id)
    if not book:
        return jsonify({'error': 'Not found'})
    book.reviews = request.json["reviews"]
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/edit_status/<user_id>', methods=['PUT'])
def edit_status(user_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    user.books = request.json["books"]
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/add_book/', methods=['GET'])
def web_add_book():
    name = request.args.get('author_name')
    surname = request.args.get('author_surname')
    if (name == 'Я' and not db.get_author(name, surname)) or name == 'Другое':
        return jsonify({'is_new_author': True})
    else:
        add_book_in_db(request.args)
        return jsonify({'is_new_author': False})


def add_book_in_db(form: dict):
    book = Library(
        name=form.get('name'),
        author_id=db.get_author(form.get('author_name'),
                                form.get('author_surname')).id,
        picture=form.get('picture'),
        genre=form.get('genre'),
        summary=form.get('summary'),
        history_of_creation=form.get('history_of_creation'),
        link_to_the_book=form.get('link_to_the_book'),
        link_to_the_production=form.get('link_to_the_production'),
        link_to_audio=form.get('link_to_audio'),
        link_to_the_screenshot=form.get('link_to_the_screenshot'))

    db_sess = db_session.create_session()
    db_sess.add(book)
    db_sess.commit()


@blueprint.route('/api/add_author', methods=['PUT'])
def add_author():
    form = request.args
    author = Authors(
        name=form.get('name'),
        surname=form.get('surname'),
        about=form.get('about'),
        picture=form.get('picture'))

    db_sess = db_session.create_session()
    db_sess.add(author)
    db_sess.commit()

