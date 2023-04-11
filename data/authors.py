import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Authors(SqlAlchemyBase):
    __tablename__ = 'authors'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    picture = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    library = orm.relationship("Library", back_populates='authors')
