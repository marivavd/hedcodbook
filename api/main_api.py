from flask import request, jsonify, Blueprint
from data import db_session
from data.library import Library

from data.users import User
from data.authors import Authors
from random import choice
import json

blueprint = Blueprint('main_api', __name__, template_folder='templates')


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


def get_author(name, surname):
    db_sess = db_session.create_session()
    return db_sess.query(Authors).filter(Authors.name.lower() == name,
                                         Authors.surname.lower() == surname).first()


@blueprint.route('/api/add_book', methods=['POST'])
def web_add_book():
    name = request.args.get('author_name')
    surname = request.args.get('author_surname')
    if name == 'я':
        if get_author(name, surname):
            add_book_in_db(request.args)
        else:
            return 'add_author'
    elif name == 'другое':
        return 'add_author'
    else:
        id_author = get_author(name, surname)['id']
    # прописать POST запрос


def add_book_in_db(form):
    book = Library(
        name=form.name,
        author_id=get_author(form.get('author_name'),
                             form.get('author_surname')).id,
        picture=form.picture,
        genre=form.genre,
        summary=form.summary,
        history_of_creation=form.history_of_creation,
        link_to_the_form=form.link_to_the_form,
        link_to_the_production=form.link_to_the_production,
        link_to_audio=form.link_to_audio,
        link_to_the_screenshot=form.link_to_the_screenshot,
        submit=form.submit)

    db_sess = db_session.create_session()
    db_sess.add(book)
    db_sess.commit()
