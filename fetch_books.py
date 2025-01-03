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
    Saves a list of books to the database, including author, genre, number of pages,
    subjects, description, and reviews.

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
            
            # Handle genre (OpenLibrary doesn't directly provide genres, using "Unknown" for now)
            genre = Genre.query.filter_by(name="Unknown").first()
            if not genre:
                genre = Genre(name="Unknown")
                db.session.add(genre)
                db.session.commit()

            # Get the book's Open Library ID for detailed information
            ol_id = book.get('key').replace('/works/', '')
            book_details_url = f"https://openlibrary.org/works/{ol_id}.json"
            book_details_response = requests.get(book_details_url)

            if book_details_response.status_code == 200:
                book_details = book_details_response.json()

                # Extracting additional fields
                description = book_details.get('description', {}).get('value', 'No description available.')
                number_of_pages = book_details.get('number_of_pages', None)
                subjects = book_details.get('subjects', [])
                
                # Handle book title and published year
                book_title = book.get('title')
                published_year = book.get('first_publish_year', None)

                # Add book to database
                if book_title:
                    new_book = Book(
                        title=book_title,
                        description=description,
                        average_rating=book.get('average_rating', 0.0),  # If available
                        published_year=published_year,
                        number_of_pages=number_of_pages,
                        author_id=author.id if author else None,
                        genre_id=genre.id
                    )
                    db.session.add(new_book)
                    db.session.commit()

                    # Optionally add subjects (e.g., genre-based)
                    for subject in subjects:
                        # For simplicity, creating a new Genre entry if it doesn't exist
                        genre = Genre.query.filter_by(name=subject).first()
                        if not genre:
                            genre = Genre(name=subject)
                            db.session.add(genre)
                            db.session.commit()

                        # Optionally, associate subject/genre with book (depending on your design)
                        new_book.genre = genre
                        db.session.commit()

            else:
                print(f"Failed to fetch details for {book.get('title')}")
        
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
