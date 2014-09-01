from . import db


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    identified = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<Book %r>' % (self.id)


class Listing(db.Model):
    __tablename__ = 'listings'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<Listing %r>' % (self.id)


class BookEntry(db.Model):
    __tablename__ = 'book_entries'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.Unicode(2048), index=True)
    pos = db.Column(db.Integer)
    lang = db.Column(db.Unicode(128))
    format = db.Column(db.Unicode(128))
    error = db.Column(db.Boolean)

    book = db.relationship('Book', backref='entries', lazy='joined')
    listing = db.relationship('Listing', backref='entries', lazy='dynamic')
