import os

from flask import Flask, session, render_template, request, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "1acpsBDaZqg8qtyWk9BaA", "isbns": "9781632168146"})
#print(res.json())

app = Flask(__name__)



# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# sqlalchemy engine object that manages connections to the database
engine = create_engine(os.getenv("DATABASE_URL"))

# ensures users actions are kept separate
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    headline = "Welcome to the book app!"
    return render_template("index.html", headline = headline)

@app.route("/registration", methods=["POST","GET"])
def registration():

    formName = request.form.get("name")
    formPassword = request.form.get("Password1")
    formPasswordCheck = request.form.get("Password2")

    if formPassword != formPasswordCheck:
        flash("Passwords don't match! Please try again.")
        return render_template("registration.html")

    if request.method == "POST":
        checkData = db.execute("SELECT user_name FROM registered_users WHERE user_name=(:formName)",
                        {"formName":formName}).fetchone()
        if checkData != None:
            return render_template("error.html", message="User already exists.")
        else:
            db.execute("INSERT INTO registered_users (user_name, password) VALUES (:formName, :formPassword)",
                                    {"formName":formName, 
                                    "formPassword":formPassword})
            db.commit()
    

    return render_template("registration.html")
    # Start by getting form information

@app.route("/login")
def login():
<<<<<<< HEAD
    # Login will need to check that the user exists, and present an error if they don't.
    # If they do exist, then it will need to verify that they put in the right password.
    # Then it will need to create the session assign to that user.







=======
>>>>>>> 4aad453f1619afd28c9488f13d307f4a89a70a89
    return(render_template("login.html"))

@app.route("/bottles")
def bottles():
    return(render_template("bottles.html"))

@app.route("/pickabook")
def pickabook():
    return render_template("pickabook.html")
<<<<<<< HEAD

=======
>>>>>>> 4aad453f1619afd28c9488f13d307f4a89a70a89


@app.route("/registrationSuccess", methods=["POST","GET"])
def registrationMessage(email):
    email = request.form.get("email")
    # Code here will check if email exists in server, and conditionally return a success message if email is already in system or not



