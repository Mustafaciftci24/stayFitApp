from flask import Flask, render_template
import psycopg2
app = Flask(__name__)


def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='postgres',
                            user="postgres",
                            password="Mustafa2323")
    return conn


@app.route("/")
@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * from \"Company\".\"Department\"")
    books = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("register.html", books=books )

