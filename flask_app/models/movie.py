import os
from sqlite3 import DatabaseError, connect
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash, url_for,request
from werkzeug.utils import secure_filename 
from flask_app import app
from flask_app.models import user

UPLOAD_FOLDER = 'flask_app/static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class Movie:

    database_name = "mydb"

    def __init__(self,data):
        self.id = data["id"]
        self.title = data["title"]
        self.genre = data["genre"]
        self.rating = data["rating"]
        self.note = data["note"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.release_year = data["release_year"]
        self.watch_date = data["watch_date"]
        self.user = None

    @classmethod
    def create_movie(cls,data):
        if not cls.validate_movie(data):
            return False
        # file = request.files['file']
        # filename = secure_filename(file.filename)
        # save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # file.save(save_path) 
        query = """
                INSERT INTO movies (title,genre,rating,note, user_id,release_year,watch_date) 
                VALUES (%(title)s, %(genre)s, %(rating)s, %(note)s, %(user_id)s, %(release_year)s, %(watch_date)s);
                """
        movie_id = connectToMySQL(cls.database_name).query_db(query,data)
        movie = cls.get_movie_by_id(movie_id)
        return movie

    @classmethod
    def delete_movie(cls,data):
        data = {"id" : data}
        query = """
                DELETE FROM movies WHERE id = %(id)s;
                """
        return connectToMySQL(cls.database_name).query_db(query,data)
    
    @classmethod
    def get_movie_by_id(cls,movie_id):
        data = {"id" : movie_id}
        query = """
                SELECT movies.id, movies.created_at, movies.updated_at, title, genre, rating, note,release_year,watch_date,
                    users.id as user_id, first_name, last_name, email, users.created_at as user_created_at, users.updated_at as user_updated_at, users.password as user_password
                    FROM movies
                    JOIN users on users.id = movies.user_id
                    WHERE movies.id = %(id)s;
                """
        result = connectToMySQL(cls.database_name).query_db(query,data)
        result = result[0]
        movie = cls(result)

        movie.user = user.User(
                {
                    "id": result["user_id"],
                    "first_name": result["first_name"],
                    "last_name": result["last_name"],
                    "email": result["email"],
                    "created_at": result["user_created_at"],
                    "updated_at": result["user_updated_at"],
                    "password": result["user_password"]
                }
            )
        return movie

    @classmethod
    def get_all_movie_and_user(cls):
        query = """
                SELECT 
                movies.id, movies.created_at, movies.updated_at, title, genre, rating, note, release_year, watch_date,
                users.id as user_id, first_name, last_name, email, users.created_at as user_created_at, users.updated_at as user_updated_at, users.password as user_password
                FROM movies
                JOIN users on users.id = movies.user_id;
                """
        results = connectToMySQL(cls.database_name).query_db(query)
        all_movies = []
        for movie in results:
            movie_object = cls(movie)
            movie_object.user = user.User(
                {
                    "id": movie["user_id"],
                    "first_name": movie["first_name"],
                    "last_name": movie["last_name"],
                    "email": movie["email"],
                    "created_at": movie["user_created_at"],
                    "updated_at": movie["user_updated_at"],
                    "password": movie["user_password"]
                }
            )
            all_movies.append(movie_object)
        return all_movies
    
    @classmethod
    def update_movie(cls, data, session_id):
        if not cls.validate_movie(data):
            return False
        query = """
                UPDATE movies 
                SET title = %(title)s, genre = %(genre)s, rating = %(rating)s, note = %(note)s, release_year = %(release_year)s, watch_date = %(watch_date)s
                WHERE id = %(id)s;
                """
        result = connectToMySQL(cls.database_name).query_db(query,data)
        movie = cls.get_movie_by_id(data["id"])
        return movie
    
    @staticmethod
    def validate_movie(data):
        valid = True
        if len(data["title"]) <= 0:
            flash("Title is required")
            valid = False
        return valid

