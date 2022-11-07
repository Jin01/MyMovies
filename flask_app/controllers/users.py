from flask_app import app
from flask import Flask, render_template, request, redirect,session
from flask_app.models.user import User 
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('login_registration.html')

@app.route('/register',methods=['POST'])
def register():
    valid_user  = User.validate_registration(request.form)
    if not valid_user:
        return redirect("/")
    data = {
        "first_name":request.form["first_name"],
        "last_name":request.form["last_name"],
        "email":request.form["email"],
        "password":bcrypt.generate_password_hash(request.form["password"])
    }
    session["user_id"] = User.register_user(data)
    return redirect("/movies/dashboard")

@app.route('/login',methods=["POST"])
def login():
    valid_user = User.validate_login(request.form)
    if not valid_user:
        return redirect("/")
    session["user_id"] = valid_user.id
    return redirect("/movies/dashboard")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')