from flask import render_template
from app import app

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("createaccount.html")

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgotpassword.html")

@app.route("/intro")
def intro():
    return render_template("intropage.html")
