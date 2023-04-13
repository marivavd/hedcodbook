from flask import request, jsonify, Blueprint
from data import db_session
from data.library import Library
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

    if search and search != 'None':
        # Если поле не заполнено, то html выбрасывает 'None'
        # если аргумент не передан, то python выбрасывает None
        # оба случая не должны попасть в фильтр
        books = filter_book(books, book_filter, search)

    books.sort(key=lambda i: (-i.summa_marks / i.count_marks, -i.count_marks))
    return json.dumps(books, default=lambda x: x.get_json_dict())
