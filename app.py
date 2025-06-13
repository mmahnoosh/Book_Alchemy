from flask import Flask, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book
import datetime
import os

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'library.sqlite')}"

db.init_app(app)


def check_date_validity(input_date):
    try:
        return datetime.datetime.strptime(input_date,"%Y-%m-%d")
    except ValueError:
        return "Error!"





@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        birthdate = request.form.get("birthdate")
        date_of_death = request.form.get("date_of_death")
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

    return render_template("add_author.html")

@app.errorhandler(400)
def bad_request(error):
    return render_template("error.html", error=error)


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", error=error)
"""
Create a Flask route called /add_author that renders the add_author.html form used to gather 
information about an author when a GET request comes in, and adds a new author record to the database using SQLAlchemy when a POST request comes in. 
When a new author has successfully been added to the database, a success message should be displayed on the /add_author page.
Note that because you created an autoincrementing Primary Key for the id column of the Author model, you do not need to show a text field in the form for the user to insert their own author id."""