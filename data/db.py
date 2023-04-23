from data.authors import Authors
from data.library import Library
from data.users import User
from data import db_session


class MyDataBase:
    def __init__(self):
        db_session.global_init("db/library.db")
        self.db_sess = db_session.create_session()

    def get_sp_authors(self):
        return self.db_sess.query(Authors).all()

    def check_email(self, email):
        return self.db_sess.query(User).filter(User.email == email).first()

    def get_author(self, name, surname):
        print([name, surname])
        for i in self.db_sess.query(Authors).all():
            if my_str(i.name) == my_str(name) and my_str(i.surname) == my_str(surname):
                q = i
        return self.db_sess.query(Authors).filter(my_str(Authors.name) == my_str(name),
                                                  my_str(Authors.surname) == my_str(surname)).first()

    def check_book(self, name):
        return self.db_sess.query(Library).filter(my_str(Library.name) == my_str(name)).first()

    def check_nickname(self, nickname):
        return self.db_sess.query(User).filter(User.nickname == nickname).first()


def my_str(stra):
    return str(stra).strip().lower()
