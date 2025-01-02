import spacy
from models import Book

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def get_recommendations(query, books, top_n=10):
    if not query:
        return []

    # Process the query with spaCy
    query_doc = nlp(query)

    # Compute similarity scores
    recommendations = []
    for book in books:
        # Combine description and tags for analysis
        text = (book.description or '') + ' ' + (book.tags or '')
        book_doc = nlp(text)

        # Compute similarity
        similarity = query_doc.similarity(book_doc)
        recommendations.append((book, similarity))

    # Sort by similarity score in descending order
    recommendations.sort(key=lambda x: x[1], reverse=True)

    return [book for book, _ in recommendations[:top_n]]