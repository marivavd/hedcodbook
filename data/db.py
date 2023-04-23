from data.authors import Authors
from data.library import Library
from data.users import User
from data import db_session


class MyDataBase:
    def _init_(self):
        db_session.global_init("db/library.db")
        self.db_sess = db_session.create_session()

    def get_sp_authors(self):
        return self.db_sess.query(Authors).all()

    def check_email(self, email):
        return self.db_sess.query(User).filter(User.email == email).first()

    def check_author(self, name, surname):
        return self.db_sess.query(Authors).filter(Authors.name.lower() == name.lower(),
                                                  Authors.surname.lower() == surname.lower()).first()

    def check_book(self, name):
        return self.db_sess.query(Library).filter(Library.name.lower() == name.lower()).first()

    def get_nickname(self, nickname):
        return self.db_sess.query(User).filter(User.nickname == nickname).first()