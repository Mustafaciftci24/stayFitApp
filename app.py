from flask import Flask, render_template, request, Response, make_response, jsonify
import psycopg2
import os
app = Flask(__name__)


def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='postgres',
                            user="postgres",
                            password="Mustafa2323")
    return conn


conn = get_db_connection()
cur = conn.cursor()


@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email=request.form.get("email")
        password = request.form.get("password")
        return f"Successful {email} {password}"
    return render_template("login.html")


@app.route("/register", methods=['GET', 'POST'])
@app.errorhandler(401)
def register():
    if request.method == "POST":
        fname = request.form.get("firstname")
        lname = request.form.get("lastname")
        password = request.form.get("pass")
        if password != request.form.get("pass-confirm"):
            return render_template("error401.html"),401
        return f"{password}"
    return render_template("register.html")
