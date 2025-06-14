from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DATE

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    birth_date = Column(DATE, nullable=False)
    date_of_death = Column(DATE, nullable=True)

    books = db.relationship("Book", back_populates="author")

    def __repr__(self):
        return (f"id: {self.id} name:{self.name} birth_date:{self.birth_date} "
                f"date_of_death:{self.date_of_death}")

    def __str__(self):
        if not self.date_of_death:
            return f"name:{self.id} birth_date:{self.birth_date}"
        return f"name:{self.id} birth_date:{self.birth_date} date_of_death:{self.date_of_death}"


class Book(db.Model):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, autoincrement=True)
    isbn = Column(String(20), nullable=False, unique=True)
    title = Column(String(100), nullable=False, unique=True)
    publication_year = Column(Integer, nullable=False)
    author_id = Column(Integer, db.ForeignKey("authors.id"))
    cover_image = Column(String(200))
    author = db.relationship("Author", back_populates="books")

    def __repr__(self):
        return (f"id: {self.id} isbn_: {self.isbn} title:{self.title} "
                f"publication_year:{self.publication_year} author_id:{self.author_id}")

    def __str__(self):
        return (f"isbn_: {self.isbn} title:{self.title} "
                f"publication_year:{self.publication_year}")
