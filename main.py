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

# Viewing a page of someones' quotes
@app.route("/quotes/<int:person_id>", methods=["GET"])
def quotes(person_id):
    # gets data of all quotes from person_id in the api
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT name FROM Person WHERE id = ?''', (person_id,))
    name = cursor.fetchone()
    cursor.execute('''SELECT description FROM Person WHERE id = ?''', (person_id,))
    descrip = cursor.fetchone()
    cursor.execute('''SELECT text FROM Quote WHERE person_id = ?''',
                   (person_id,))
    quote_text = cursor.fetchall()
    return render_template("quotes.html",
                           name=name[0], quote_text=quote_text, 
                           descrip=descrip[0])

# This is just error 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)