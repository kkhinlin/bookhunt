from flask import Flask, request, jsonify, render_template
from models import db, Book, Review, Genre, Author, UserBooks
from schemas import BookSchema, ReviewSchema, GenreSchema, AuthorSchema
from config import Config
from recommendations import get_recommendations, record_feedback  # Import the record_feedback function
from routes import api
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Marshmallow schemas
book_schema = BookSchema()
books_schema = BookSchema(many=True)
review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)
author_schema = AuthorSchema()

# Use app context to create tables at startup
with app.app_context():
    db.create_all()

# Register the API blueprint
app.register_blueprint(api)

# API Routes
# Books Routes
@app.route('/api/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return books_schema.jsonify(books)

@app.route('/api/books/<string:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return book_schema.jsonify(book)

# Reviews Routes
@app.route('/api/reviews', methods=['POST'])
def add_review():
    data = request.get_json()
    book_id = data.get('book_id')
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    review = Review(book_id=book_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    
    return review_schema.jsonify(review), 201

@app.route('/api/reviews/book/<string:book_id>', methods=['GET'])
def get_reviews(book_id):
    reviews = Review.query.filter_by(book_id=book_id).all()
    return reviews_schema.jsonify(reviews)

# Genres Routes
@app.route('/api/genres', methods=['GET'])
def get_genres():
    genres = Genre.query.all()
    return genres_schema.jsonify(genres)

# Authors Routes
@app.route('/api/authors/<string:author_id>', methods=['GET'])
def get_author(author_id):
    author = Author.query.get_or_404(author_id)
    return author_schema.jsonify(author)

# Book Recommendation Route
@app.route('/api/recommend', methods=['GET'])
def recommend_books():
    query = request.args.get('query', '').strip()
    genre = request.args.get('genre', '')  # You can filter by genre here if desired
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    # Get past books the user has interacted with
    user_books = UserBooks.query.filter_by(status="read").all()
    books = Book.query.all()
    
    # Generate recommendations
    recommended_books = get_recommendations(query, books, user_books, genre)
    
    return books_schema.jsonify(recommended_books)

# Feedback Route
@app.route('/api/feedback', methods=['POST'])
def handle_feedback():
    data = request.get_json()
    user_id = data.get('user_id')
    book_id = data.get('book_id')
    feedback = data.get('feedback')  # 'accept' or 'reject'
    
    # Store feedback using the new function
    record_feedback(user_id, book_id, feedback)
    
    return jsonify({"message": "Feedback recorded successfully"}), 200

# Frontend Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/recommendations', methods=['GET'])
def recommendations_page():
    query = request.args.get('query', '').strip()
    genre = request.args.get('genre', '').strip()

    print(f"Query: {query}, Genre: {genre}")  # For debugging

    # Get past books the user has interacted with
    user_books = UserBooks.query.filter_by(status="read").all()
    books = Book.query.all()

    recommended_books = get_recommendations(query, books, user_books, genre) if query else []

    # Debugging: Print the number of recommended books
    print(f"Number of recommendations: {len(recommended_books)}")

    return render_template('recommendations.html', books=recommended_books, query=query, genre=genre)

@app.route('/past_reads', methods=['GET', 'POST'])
def past_reads_page():
    if request.method == 'POST':
        # Get data from the request
        data = request.get_json()
        book_id = data.get('book_id')
        opinion = data.get('opinion', '')

        if not book_id:
            return jsonify({"error": "Book ID is required"}), 400

        # Check if the book is already added for the user
        existing_user_book = UserBooks.query.filter_by(book_id=book_id, status="read").first()

        if existing_user_book:
            # If the book already exists, update the opinion
            existing_user_book.opinion = opinion
            db.session.commit()
            return jsonify({"message": "Opinion updated successfully"}), 200
        else:
            # If the book does not exist, add it to the database
            user_book = UserBooks(book_id=book_id, status="read", opinion=opinion)
            db.session.add(user_book)
            db.session.commit()
            return jsonify({"message": "Past read added successfully"}), 201

    # If it's a GET request, return the past reads
    user_books = UserBooks.query.filter_by(status="read").all()
    return render_template('past_reads.html', user_books=user_books)

@app.route('/reading_list', methods=['GET'])
def reading_list_page():
    user_books = UserBooks.query.filter_by(status="reading").all()
    return render_template('reading_list.html', user_books=user_books)

@app.route('/book/<string:book_id>', methods=['GET'])
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_details.html', book=book)

if __name__ == '__main__':
    app.run(debug=True)