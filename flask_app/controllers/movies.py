from flask_app import app
from flask import Flask, render_template, request, redirect,session
from flask_app.models.user import User 
from flask_app.models.movie import Movie


@app.route("/movies/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    user = User.get_one_user_by_id(session["user_id"])
    all_movies = Movie.get_all_movie_and_user()

    return render_template("dashboard.html",user=user,all_movies=all_movies)

@app.route("/movies/new")
def add_page():
    if "user_id" not in session:
        return redirect("/")
    return render_template("new_movie.html")

@app.route("/movies/create",methods=["POST"])
def add_movie():
    if "user_id" not in session:
        return redirect("/")
    valid = Movie.create_movie(request.form)
    if valid:
        return redirect('/movies/dashboard')
    return redirect('/movies/new')

@app.route("/movies/show/<int:id>")
def movie_detail(id):
    user = User.get_one_user_by_id(session["user_id"])
    movie = Movie.get_movie_by_id(id)
    return render_template("/show_movie.html", movie=movie, user=user)

@app.route("/movies/account")
def account():
    if "user_id" not in session:
        return redirect("/")
    user_movies = User.get_all_movie_of_one_user(session["user_id"])
    return render_template("account.html",user_movies=user_movies)

@app.route("/movies/delete/<int:id>")
def delete_movie(id):
    Movie.delete_movie(id)
    return redirect("/movies/account")

@app.route("/movies/edit/<int:id>")
def edit_movie(id):
    if "user_id" not in session:
        return redirect("/")
    movie = Movie.get_movie_by_id(id)
    return render_template("edit_movie.html",movie=movie)

@app.route("/movies/update/<int:id>",methods=["POST"])
def update_movie(id):
    valid_movie = Movie.update_movie(request.form, session["user_id"])
    if not valid_movie:
        return redirect(f'/movies/account')
    return redirect("/movies/account")
