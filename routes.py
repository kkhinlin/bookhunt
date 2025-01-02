from flask import Blueprint, request, jsonify
from models import db, Book, UserBooks

api = Blueprint('api', __name__)

@api.route('/api/past_reads', methods=['POST'])
def add_past_read():
    data = request.get_json()
    book_id = data.get('book_id')
    status = data.get('status')
    opinion = data.get('opinion', '')

    if not book_id or not status:
        return jsonify({'error': 'book_id and status are required'}), 400

    # Add to UserBooks
    user_book = UserBooks(book_id=book_id, status=status, opinion=opinion)
    db.session.add(user_book)
    db.session.commit()

    return jsonify({'message': 'Past read added successfully'}), 201

@api.route('/api/past_reads', methods=['GET'])
def view_past_reads():
    user_books = UserBooks.query.all()
    result = [
        {
            'id': user_book.id,
            'book_id': user_book.book_id,
            'status': user_book.status,
            'opinion': user_book.opinion
        }
        for user_book in user_books
    ]
    return jsonify(result), 200
