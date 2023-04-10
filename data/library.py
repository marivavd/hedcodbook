import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Library(SqlAlchemyBase):
    __tablename__ = 'library'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("authors.id"))
    picture = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    genre = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    link_to_the_production = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='no_information')
    link_to_the_book = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='no_information')
    link_to_audio = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='no_information')
    link_to_the_screenshot = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='no_information')
    summary = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    history_of_creation = sqlalchemy.Column(sqlalchemy.Text, nullable=True)

    summa_marks = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    count_marks = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    reviews = sqlalchemy.Column(sqlalchemy.JSON, default={})
    authors = orm.relationship('Authors')
