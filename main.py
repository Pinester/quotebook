from flask import Flask, render_template, request, redirect, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
# Random generated key to confirm indivdiual user session
# print(os.urandom(24).hex())
SECRET_KEY = "184989dcf7e442d9550c4c9e228f9a752cde4045d9ddb19d"
app.secret_key = SECRET_KEY

def get_db():
    # Stores DB connection to a variable. Prevents crashing and db locking.
    if "db" not in g:
        g.db = sqlite3.connect("quotes.db")
    return g.db

# Closes database connection when website goes down
@app.teardown_appcontext
def teardown_db(_):
    get_db().close()


def is_logged_in():
    # Checks if user is logged in (aka session)
    return session.get("is_logged_in", False)


# Home page (wow)
@app.route("/")
def home():
    get_db()
    return render_template("home.html")


# Viewing a page of someones' quotes
@app.route("/quotes/<int:person_id>", methods=["GET"])
def quotes(person_id):
    # gets data of all quotes from person_id in the api
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT name FROM Person WHERE id = ?''', (person_id,))
    name = cursor.fetchone()
    cursor.execute('''SELECT image_string FROM Person WHERE id = ?''', (person_id,))
    image = cursor.fetchone()
    cursor.execute('''SELECT description FROM Person WHERE id = ?''', (person_id,))
    descrip = cursor.fetchone()
    cursor.execute('''SELECT text FROM Quote WHERE person_id = ?''',
                   (person_id,))
    quote_text = cursor.fetchall()
    return render_template("quotes.html",
                           name=name[0], image=image, quote_text=quote_text, 
                           descrip=descrip[0])

# This is just error 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

# Signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # Requests database to modify to add the details of the newly made account.
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hashpassword = generate_password_hash(password)
        conn = get_db()
        cursor = conn.cursor()
        # check username is unique
        cursor.execute('''SELECT username FROM User WHERE username = ?''',
                       (username,))
        usernamecheck = cursor.fetchone()
        print(usernamecheck)
        if usernamecheck is not None:
            print("test")
            return render_template("signup.html",
                                   error="Existing account has this username.")
        # inserting new account into db
        cursor.execute('''INSERT INTO User
                        (username, password_hash, admin)
                        VALUES (?,?,0)
                        ''', (username, hashpassword))
        conn.commit()
        # selecting user_id to validate session
        cursor.execute('''SELECT id FROM User WHERE username = ?''',
                       (username,))
        user_id = cursor.fetchone()
        session["user_id"] = user_id
        conn.close
        session["is_logged_in"] = True
        return redirect("/")
    return render_template("signup.html")


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    # Requests db to see if acc exists
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''SELECT id FROM User WHERE username = ?''',
                       (username,))
        user_id = cursor.fetchone()
        if user_id is None:
            return render_template("login.html",
                                   error="Account not found.")
            # If account is not found then it stops rest of code to execute
        cursor.execute('''SELECT password_hash FROM User WHERE id = ?''',
                       (user_id[0],))
        # Checks to see if password is correct
        passfetch = cursor.fetchone()[0]
        if not check_password_hash(passfetch, password):
            return render_template("login.html", error="Password Incorrect.")
        cursor.execute('''SELECT id FROM User WHERE username = ?''',
                       (username,))
        user_id = cursor.fetchone()
        session["user_id"] = user_id
        # Gives admin session to the one admin account
        cursor.execute('''SELECT admin FROM User WHERE username = ?''',
                       (username,))             
        admin_check = cursor.fetchone()
        admin_check = admin_check[0]  
        if admin_check == (1):
            session["admin"] = True
        else:
            session["admin"] = False
        session["is_logged_in"] = True
        return redirect("/")
    return render_template("login.html")
    # Fetches SQL to see if the password matches username.

# Submit a Quote. Should only be accessible if logged in.
@app.route("/addquote", methods=["GET", "POST"])
def addquote():
    if session.get("user_id") is not None:
        return render_template("addquote.html")
    else:
        return redirect("/login")


@app.route("/logout")
def logout():
    # ends user session
    session.pop("is_logged_in", False)
    session.pop("user_id", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)

