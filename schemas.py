from marshmallow import Schema, fields

class AuthorSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    bio = fields.Str()

class GenreSchema(Schema):
    id = fields.Str()
    name = fields.Str()

class BookSchema(Schema):
    id = fields.Str()
    title = fields.Str()
    description = fields.Str()
    average_rating = fields.Float()
    published_year = fields.Int()
    author = fields.Nested(AuthorSchema)
    genre = fields.Nested(GenreSchema)

class ReviewSchema(Schema):
    id = fields.Str()
    rating = fields.Int()
    comment = fields.Str()
    created_at = fields.DateTime()
    book_id = fields.Str()
