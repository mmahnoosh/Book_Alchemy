import datetime
import os

from flask import Flask, render_template, request, abort, jsonify
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from data_models import db, Author, Book

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'library.sqlite')}"

db.init_app(app)


def check_date_validity(input_date):
    """
        Validates a date string in 'YYYY-MM-DD' format.
        Returns a datetime.date object if valid, otherwise None.
    """
    try:
        return datetime.datetime.strptime(input_date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def check_lifespan_validity(birthdate, date_of_death):
    """
      Checks if the date of death is after the birthdate.
      Returns "Error!" if the lifespan is invalid, otherwise an empty string.
    """
    if (date_of_death - birthdate).total_seconds() < 0:
        return "Error!"
    return ""


@app.route("/", methods=["GET"])
def home():
    """
        Handles the home page request with optional search and sorting.
        Retrieves books with optional filtering by title or author name,
        sorts by title or author, and renders the home template with the results.
    """
    search_query = request.args.get("search_query", "")
    sort_by = request.args.get("sort_by", "title")

    # Start a SQLAlchemy query with Join
    query = db.session.query(Book.id, Book.title, Author.name.label("author"), Book.isbn).join(
        Author)

    # Optional filter: Search in title **or** author name
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Book.title.ilike(search_term),
                Author.name.ilike(search_term)
            )
        )

    # Sort by author or title
    if sort_by == "author":
        query = query.order_by(Author.name, Book.title)
    else:
        query = query.order_by(Book.title, Author.name)

    # Execute query
    books_raw = query.all()

    # Convert tuples to dictionaries
    books = [
        {"id": id, "title": title, "author": author, "isbn": isbn}
        for id, title, author, isbn in books_raw
    ]

    # Passing to the template
    return render_template("home.html", books=books,
                           sort_by=sort_by, search_query=search_query)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """
        Fügt einen neuen Autor hinzu.
        Bei GET wird das Formular angezeigt, bei POST werden die Formulardaten validiert
        und gespeichert.
        Gibt bei Erfolg eine Bestätigung oder bei Fehlern einen HTTP-400-Fehler zurück.
    """
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        birthdate = request.form.get("birthdate")
        date_of_death = request.form.get("date_of_death") or None
        if not name:
            abort(400, description="Name is required")
        if not birthdate:
            abort(400, description="birthdate is required")
        birthdate = check_date_validity(birthdate)
        if birthdate == "Error!":
            abort(400, description="birthdate needs to be format 'YYYY-MM-DD'")
        if date_of_death:
            date_of_death = check_date_validity(date_of_death)
            if date_of_death == "Error!":
                abort(400, description="date of death needs to be format 'YYYY-MM-DD'")
            if check_lifespan_validity(birthdate, date_of_death) == "Error!":
                abort(400, description="date of death cannot occur before birthdate")

        author = Author(
            name=name,
            birth_date=birthdate,
            date_of_death=date_of_death
        )
        try:
            db.session.add(author)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, description="Name need to be unique")
        except SQLAlchemyError:
            db.session.rollback()
            abort(400, description="Error with the database. Please try again")
        return f"{author.name} added successfully"

    return render_template("add_author.html")


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """
       Handles adding a new author via form submission.

       Validates input data, checks date formats and lifespan logic,
       saves the author to the database if valid, and handles errors appropriately.
    """
    authors = Author.query.order_by(Author.name).all()
    if request.method == "POST":
        isbn = request.form.get("isbn", "").strip()
        title = request.form.get("title", "").strip()
        publication_year = request.form.get("publication_year")
        author_id = request.form.get("author_id")

        if not title:
            abort(400, description="Title is required")
        if not isbn:
            abort(400, description="ISBN is required")
        if not publication_year:
            abort(400, description="Publication year is required")
        if not author_id:
            abort(400, description="Author id is required")

        book = Book(
            isbn=isbn,
            title=title,
            publication_year=publication_year,
            author_id=author_id
        )
        try:
            db.session.add(book)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, description="Title and ISBN need to be unique")
        except SQLAlchemyError:
            db.session.rollback()
            abort(400, description="Error with the database. Please try again")
        return f"{book.title} added successfully"

    return render_template("add_book.html", authors=authors)


@app.route("/seed")
def seed_data():
    """
        Populates the database with initial authors and books data.

        Checks for existing entries to avoid duplicates,
        validates dates, and commits all new records to the database.
    """
    authors_data = [
        {
            "name": "George Orwell",
            "birth_date": "1903-06-25",
            "date_of_death": "1950-01-21"
        },
        {
            "name": "J.K. Rowling",
            "birth_date": "1965-07-31",
            "date_of_death": ""
        },
        {
            "name": "Jane Austen",
            "birth_date": "1775-12-16",
            "date_of_death": "1817-07-18"
        },
        {
            "name": "Ernest Hemingway",
            "birth_date": "1899-07-21",
            "date_of_death": "1961-07-02"
        },
        {
            "name": "Franz Kafka",
            "birth_date": "1883-07-03",
            "date_of_death": "1924-06-03"
        },
        {
            "name": "Haruki Murakami",
            "birth_date": "1949-01-12",
            "date_of_death": ""
        },
        {
            "name": "Leo Tolstoy",
            "birth_date": "1828-09-09",
            "date_of_death": "1910-11-20"
        }
    ]

    books_data = [
        {
            "title": "1984",
            "isbn": "9780451524935",
            "publication_year": 1949,
            "author": "George Orwell"
        },
        {
            "title": "Harry Potter and the Philosopher's Stone",
            "isbn": "9780747532699",
            "publication_year": 1997,
            "author": "J.K. Rowling"
        },
        {
            "title": "Pride and Prejudice",
            "isbn": "9780141439518",
            "publication_year": 1813,
            "author": "Jane Austen"
        },
        {
            "title": "The Old Man and the Sea",
            "isbn": "9780684801223",
            "publication_year": 1952,
            "author": "Ernest Hemingway"
        },
        {
            "title": "The Trial",
            "isbn": "9780805209990",
            "publication_year": 1925,
            "author": "Franz Kafka"
        },
        {
            "title": "Norwegian Wood",
            "isbn": "9780375704024",
            "publication_year": 1987,
            "author": "Haruki Murakami"
        },
        {
            "title": "Anna Karenina",
            "isbn": "9780143035008",
            "publication_year": 1878,
            "author": "Leo Tolstoy"
        }
    ]

    authors = {}
    for data in authors_data:
        name = data["name"]
        birth_date = check_date_validity(data["birth_date"])
        date_of_death = check_date_validity(data["date_of_death"])

        existing = Author.query.filter_by(name=name).first()
        if not existing:
            author = Author(
                name=name,
                birth_date=birth_date,
                date_of_death=date_of_death
            )
            db.session.add(author)
            db.session.flush()
            authors[name] = author
        else:
            authors[name] = existing

    db.session.commit()

    for book in books_data:
        existing_book = Book.query.filter_by(title=book["title"]).first()
        if not existing_book:
            author = authors.get(book["author"])
            if not author:
                return f"Author '{book['author']}' not found."

            new_book = Book(
                title=book["title"],
                isbn=book["isbn"],
                publication_year=book["publication_year"],
                author_id=author.id
            )
            db.session.add(new_book)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return f"Error inserting data: {str(e)}"

    return "Seed data added successfully!"


@app.route("/book/<int:book_id>/delete", methods=['POST'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    print(book)
    if not book:
        return jsonify({"error": "Book not found!"}), 404

    try:
        db.session.delete(book)
        db.session.commit()
        return jsonify({"message": "Book deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred during deletion."}), 500


@app.errorhandler(400)
def bad_request(error):
    return render_template("error.html", error=error)


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
