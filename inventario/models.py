from . import db

from sqlalchemy.orm import backref
from sqlalchemy.ext.hybrid import hybrid_property


class Model(db.Model):
    __abstract__ = True

    @classmethod
    def get_or_create(cls, id, **kwargs):
        return cls.query.get(id) or cls(id=id, **kwargs)

    @classmethod
    def find(cls, **filters):
        return cls.query.filter(**filters)

    @classmethod
    def find_one(cls, **filters):
        return cls.find(**filters).first()

    @classmethod
    def find_or_create(cls, data, **filters):
        return cls.find_one(**filters) or cls(**data)


class Book(Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    identified = db.Column(db.Boolean)

    first_entry_id = db.Column(db.Integer, db.ForeignKey('book_entries.id'))
    first_entry = db.relationship('BookEntry',
        backref=backref('is_first_entry', uselist=False),
        foreign_keys=[first_entry_id], post_update=True)

    last_entry_id = db.Column(db.Integer, db.ForeignKey('book_entries.id'))
    last_entry = db.relationship('BookEntry',
        backref=backref('is_last_entry', uselist=False),
        foreign_keys=[last_entry_id], post_update=True)

    def __repr__(self):
        return '<Book %r>' % (self.id)


class Listing(Model):
    __tablename__ = 'listings'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)

    def __repr__(self):
        return '<Listing %r>' % (self.id)


class BookEntry(Model):
    __tablename__ = 'book_entries'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(2048), index=True)
    pos = db.Column(db.Integer)
    lang = db.Column(db.Unicode(128))
    format = db.Column(db.Unicode(128))
    error = db.Column(db.Boolean)

    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    book = db.relationship(Book, backref='entries', lazy='joined', foreign_keys=[book_id])

    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'))
    listing = db.relationship(Listing, backref='entries', lazy='joined')

    @hybrid_property
    def is_first(self):
        return self.id == self.book.first_entry_id

    @hybrid_property
    def is_last(self):
        return self.id == self.book.last_entry_id

    @hybrid_property
    def repeated(self):
        return self.query.filter_by(
            listing_id=self.listing_id, book_id=self.book_id).count() > 1

    is_repeated = repeated

    def __repr__(self):
        return '<BookEntry %r for %r in %r>' % (self.id, self.book, self.listing)
