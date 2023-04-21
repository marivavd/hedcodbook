from users import User
from authors import Authors
from library import Library
from data import db_session


class MyDataBase:
    def __init__(self):
        self.db_sess = db_session.create_session()

    def get_sp_authors(self):
        return self.db_sess.query(Authors).all()

    def check_author(self, name, surname):
        return self.db_sess.query(Authors).filter(Authors.name.lower() == name.lower(),
                                                  Authors.surname.lower() == surname.lower()).first()

    def check_book(self, name):
        return self.db_sess.query(Library).filter(Library.name.lower() == name.lower()).first()
