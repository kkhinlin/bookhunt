from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    average_rating = db.Column(db.Float, default=0.0)
    published_year = db.Column(db.Integer)
    
    # Foreign Keys
    author_id = db.Column(db.String(36), db.ForeignKey('authors.id'))
    genre_id = db.Column(db.String(36), db.ForeignKey('genres.id'))

    # Relationships
    author = db.relationship('Author', backref=db.backref('books', lazy=True))
    genre = db.relationship('Genre', backref=db.backref('books', lazy=True))

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    book_id = db.Column(db.String(36), db.ForeignKey('books.id'))

    # Relationships
    book = db.relationship('Book', backref=db.backref('reviews', lazy=True))

class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), nullable=False)

class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)

class UserBooks(db.Model):
    __tablename__ = 'user_books'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    book_id = db.Column(db.String(36), db.ForeignKey('books.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # E.g., "read", "reading", "wishlist"
    opinion = db.Column(db.Text)

    # Relationships
    book = db.relationship('Book', backref=db.backref('user_books', lazy=True))
