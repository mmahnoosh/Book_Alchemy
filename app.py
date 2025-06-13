import datetime
import os

from flask import Flask, render_template, request, abort

from data_models import db, Author, Book
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'library.sqlite')}"

db.init_app(app)


def check_date_validity(input_date):
    try:
        return datetime.datetime.strptime(input_date, "%Y-%m-%d").date()
    except ValueError:
        return "Error!"


def check_lifespan_validity(birthdate, date_of_death):
    if (date_of_death - birthdate).total_seconds() < 0:
        return "Error!"
    return ""


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
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
            abort(400, desciption="Name need to be unique")
        except SQLAlchemyError:
            db.session.rollback()
            abort(400, description="Error with the database. Please try again")
        return f"{author.name} added successfully"

    return render_template("add_author.html")


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
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
            abort(400, desciption="Title and ISBN need to be unique")
        except SQLAlchemyError:
            db.session.rollback()
            abort(400, description="Error with the database. Please try again")
        return f"{book.title} added successfully"

    return render_template("add_book.html", authors=authors)


@app.errorhandler(400)
def bad_request(error):
    return render_template("error.html", error=error)


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)

"""
Create a Flask route called /add_author that renders the add_author.html form used to gather 
information about an author when a GET request comes in, and adds a new author record to the database using SQLAlchemy when a POST request comes in. 
When a new author has successfully been added to the database, a success message should be displayed on the /add_author page.
Note that because you created an autoincrementing Primary Key for the id column of the Author model, you do not need to show a text field in the form for the user to insert their own author id."""
