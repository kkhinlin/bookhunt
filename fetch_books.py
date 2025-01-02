import requests
from models import db, Book, Author, Genre
from app import app

def fetch_books_from_openlibrary(query, max_results=10):
    """
    Fetches books from the OpenLibrary API based on a search query.

    Args:
        query (str): The search term.
        max_results (int): The maximum number of books to fetch.

    Returns:
        list: A list of books retrieved from the API.
    """
    url = f"https://openlibrary.org/search.json?q={query}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        books = data.get('docs', [])[:max_results]
        return books
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return []

def save_books_to_db(books):
    """
    Saves a list of books to the database.

    Args:
        books (list): A list of book dictionaries retrieved from the OpenLibrary API.
    """
    with app.app_context():
        for book in books:
            # Handle author
            author_name = book.get('author_name', [None])[0]
            if author_name:
                author = Author.query.filter_by(name=author_name).first()
                if not author:
                    author = Author(name=author_name)
                    db.session.add(author)
                    db.session.commit()
            
            # Handle genre (OpenLibrary doesn't provide genres, so using 'Unknown')
            genre = Genre.query.filter_by(name="Unknown").first()
            if not genre:
                genre = Genre(name="Unknown")
                db.session.add(genre)
                db.session.commit()

            # Add book
            book_title = book.get('title')
            published_year = book.get('first_publish_year', None)
            if book_title:
                new_book = Book(
                    title=book_title,
                    author_id=author.id if author else None,
                    genre_id=genre.id,
                    published_year=published_year
                )
                db.session.add(new_book)
        
        db.session.commit()
        print("Books saved to database!")

if __name__ == "__main__":
    # Prompt the user for a search query
    query = input("Enter a search term for books (or press Enter to use the default 'fiction'): ").strip()
    query = query if query else "fiction"  # Default to "fiction" if no input is provided
    
    # Fetch and save books
    books = fetch_books_from_openlibrary(query)
    if books:
        save_books_to_db(books)
    else:
        print("No books found or failed to fetch books.")
