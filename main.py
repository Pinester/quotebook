from flask import Flask, render_template, request, redirect, session, g
# from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)

def get_db():
    # Stores DB connection to a variable. Prevents crashing and db locking.
    if "db" not in g:
        g.db = sqlite3.connect("quotes.db")
    return g.db

# Closes database connection when website goes down
@app.teardown_appcontext
def teardown_db(_):
    get_db().close()

# Home page (wow)
@app.route("/")
def home():
    get_db()
    return render_template("home.html")


# This is just error 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)