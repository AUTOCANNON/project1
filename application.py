import os

from flask import Flask, session, render_template, request, flash, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
import json
import requests
#res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "1acpsBDaZqg8qtyWk9BaA", "isbns": isbn})


app = Flask(__name__)
app.secret_key = "eggsalad"


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
    if "user" in session:
        user = session["user"]
        headline = f"Welcome to bookapp {user}"
    else:
        headline = "Welcome to the bookapp"
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

@app.route("/login", methods=['POST','GET'])
def login():
    # Login will need to check that the user exists, and present an error if they don't.
    # If they do exist, then it will need to verify that they put in the right password.
    # Then it will need to create the session assign to that user.
    session.pop("user", None)


    if request.method == "POST":
        userName = request.form.get("Email")
        password = request.form.get("Password")
        checkUsername = db.execute("SELECT user_name FROM registered_users WHERE user_name=(:userName)",
                        {"userName":userName}).fetchone()

        #return f"<h1>{checkData}</h1>"
        
        if checkUsername == None:
            return render_template("error.html", message="User does not exist.")
        else:
            queriedPasswordResult = db.execute("SELECT password FROM registered_users WHERE user_name=(:userName)",
                        {"userName":userName}).fetchone()
            # Removes tuple garbage.
            cleanedPassword = str(queriedPasswordResult)[2:-3]

            if cleanedPassword != password:
                return render_template("error.html", message="Incorrect password")
            else:
                session["user"] = userName
                return redirect(url_for("index"))
                
    elif request.method == "GET":
        return(render_template("login.html"))
            


@app.route("/bottles")
def bottles():
    return(render_template("bottles.html"))

@app.route("/bookinspect/<isbn>", methods = ['GET'])
def pickabook(isbn):
    if request.method == "GET":
        bookInfo = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn like :isbn",
                        {"isbn":isbn}).fetchall()
        bookreviews = db.execute("SELECT reviewtext, review_user FROM book_reviews WHERE bookid like :isbn",
                     {"isbn":isbn}).fetchall()

        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "1acpsBDaZqg8qtyWk9BaA", "isbns": isbn})
        data = res.json()
        avgRating = data["books"][0]["average_rating"]
        ratingCount = data["books"][0]["ratings_count"]
        
        
        return render_template("bookinspect.html",  bookinfo = bookInfo, reviews = bookreviews, averageRating = avgRating, ratingCount = ratingCount)

    else:
        return render_template("error.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Successfully logged out")
    return render_template("index.html")

@app.route("/booksearch", methods = ['POST','GET'])
def search():
    isbn = request.form.get("isbn")
    bookTitle = request.form.get("bookTitle")    
    author = request.form.get("author")
    values = [isbn, bookTitle, author]
    # do a check on data fields being filled before querying db.
    if request.method == "POST":
        if all(v == '' for v in values):
            flash("You must enter information into a field.")
            return render_template("search.html")
        else:
            # perform search
            if isbn:
                searchColumn = 'isbn'
            elif bookTitle:
                searchColumn = 'title'
            elif author:
                searchColumn = 'author'
            searchKeyword = isbn or bookTitle.lower() or author.lower()
            searchKeyword = searchKeyword + '%'
            checkData = db.execute(f"SELECT isbn,title,author,year FROM books WHERE LOWER(author) LIKE :searchKeyword OR isbn LIKE :searchKeyword or LOWER(title) LIKE :searchKeyword", {"searchKeyword": searchKeyword }).fetchall()
            # checkData is list of lists, need to extract out the 3rd element from each list
            if checkData == []:
                flash("No results found")
                return render_template("search.html")
            else:
                return render_template("searchresults.html", results=checkData)
    else:
        return render_template("search.html")

@app.route("/submitreview/<isbn>", methods=["POST"])
def submitreview(isbn):
    # will want to insert the users information into the DB. Will also need to check if that user already submitted
    # a review for this book, so they can't insert a duplicate
    if request.method == "POST":
        if "user" in session:
            rating = request.form.get("rating")
            textReview = request.form.get("textreview")
            uid = session.get("user")

            # TODO check if both rating and reviewtext are filled out
            if '' in [textReview,rating]:
                flash("You must enter rating and review. Please search again")
                return render_template("search.html")
                return redirect("/bookinspect/ + isbn")
            else:
                reviewAlreadyExists = db.execute("SELECT bookid, user FROM book_reviews WHERE review_user = :uid and bookid = :isbn", {"uid":uid, "isbn": isbn}).fetchall()
 
                if len(reviewAlreadyExists) > 0:
                    return "<h1> you already made a review for this book </h1>"
                else:
                # Ensure user hasn't already submitted another review for the book
                    db.execute("INSERT INTO book_reviews (bookid, review_user, rating, reviewtext) VALUES (:isbn, :uid, :rating, :textReview)",
                                                {"isbn":isbn, 
                                                "uid":uid,
                                                "rating":rating,
                                                "textReview":textReview})
                    db.commit()
                    
                    bookInfo = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn like :isbn",
                        {"isbn":isbn}).fetchall()
                    bookreviews = db.execute("SELECT reviewtext, review_user FROM book_reviews WHERE bookid like :isbn",
                                {"isbn":isbn}).fetchall()

                    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "1acpsBDaZqg8qtyWk9BaA", "isbns": isbn})
                    data = res.json()
                    avgRating = data["books"][0]["average_rating"]
                    ratingCount = data["books"][0]["ratings_count"]
                    
                    
                    return render_template("bookinspect.html",  bookinfo = bookInfo, reviews = bookreviews, averageRating = avgRating, ratingCount = ratingCount)

        else:
            flash("You must login to submit reviews..")
            return render_template("login.html")
    else:
        return "<h1>oopsie</h1>"

@app.route("/api/<isbn>")
def apirequest(isbn):
    if request.method == "GET":
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "1acpsBDaZqg8qtyWk9BaA", "isbns": isbn})
        data = res.json()
        formattedData = data["books"][0]

        bookInfo = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn like :isbn",
                        {"isbn":isbn}).fetchall()
        


        queryResults = bookInfo[0]

        rTitle = queryResults[1]
        rAuthor = queryResults[2]
        rYear = queryResults[3]
        rIsbn = queryResults[0]
        reviews_count = formattedData["reviews_count"]
        average_score = formattedData["average_rating"]

        apiRes = {"title":rTitle,"author":rAuthor,"year":rYear,"isbn":rIsbn,"review_count":reviews_count,"average_score":average_score}
        
        
        #jsonRes = json.dumps(apiRes)
        #return render_template("apirequest.html", r = jsonRes)

        return jsonify(apiRes)

    else:
        abort(404)

    # {
    #     "title": "Memory",
    #     "author": "Doug Lloyd",
    #     "year": 2015,
    #     "isbn": "1632168146",
    #     "review_count": 28,
    #     "average_score": 5.0
    # }