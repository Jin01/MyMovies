from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash 
from flask_app import app
from flask_bcrypt import Bcrypt
from flask_app.models import movie
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
bcrypt = Bcrypt(app)

class User:
    database_name = "mydb"

    def __init__(self,data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.password = data['password']
        self.movies = []

    @classmethod
    def register_user(cls,data):
        query = """
        INSERT INTO users
        (first_name, last_name, email, password)
        VALUES
        (%(first_name)s, %(last_name)s, %(email)s, %(password)s);
        """
        return connectToMySQL(cls.database_name).query_db(query,data)

    @classmethod
    def get_one_user_by_email(cls,data):
        query = """
        SELECT * FROM users WHERE email = %(email)s;"""
        results = connectToMySQL(cls.database_name).query_db(query,data)
        if len(results) == 0:
            return None
        else:
            return cls(results[0])
    
    @classmethod
    def get_one_user_by_id(cls,id):
        data = {"id" : id}
        query = """
        SELECT * FROM users WHERE id = %(id)s;"""
        result = connectToMySQL(cls.database_name).query_db(query,data)
        if len(result) == 0:
            return None
        else:
            return cls(result[0])
    
    @classmethod
    def get_all_movie_of_one_user(cls,user_id):
        data = {"id" : user_id}
        query = """
                SELECT 
                users.id, users.created_at, users.updated_at, users.password, users.first_name,
                users.last_name,users.email, movies.id as movie_id, movies.created_at as movie_created_at,
                movies.updated_at as movie_updated_at, movies.title as movie_title, movies.genre as movie_genre,
                movies.rating as movie_rating, movies.note as movie_note, movies.release_year as movie_release_year, movies.watch_date as movie_watch_date
                FROM users 
                LEFT JOIN movies
                ON users.id = movies.user_id
                WHERE users.id = %(id)s;
                """
        result = connectToMySQL(cls.database_name).query_db(query,data)
        user = cls(result[0])
        for row in result:
            if row["movie_id"] == None:
                return user
            user.movies.append(movie.Movie({
                        "id": row["movie_id"],
                        "created_at": row["movie_created_at"],
                        "updated_at": row["movie_updated_at"],
                        "title": row["movie_title"],
                        "genre": row["movie_genre"],
                        "rating": row["movie_rating"],
                        "note": row["movie_note"],
                        "release_year": row["movie_release_year"],
                        "watch_date": row["movie_watch_date"]
                    }))
        return user


    @staticmethod
    def validate_login(form):
        if not EMAIL_REGEX.match(form["email"]):
            flash("Invalid login information","login")
            return False
        data = {"email":form["email"]}
        found = User.get_one_user_by_email(data)
        if found == None:
            flash("Invalid login information","login")
            return False
        if not bcrypt.check_password_hash(found.password,form["password"]):
            flash("Invalid login information","login")
            return False
        return found 
            
    @staticmethod
    def validate_registration(form):
        data = {"email":form["email"]}
        found = User.get_one_user_by_email(data)
        valid = True
        
        if len(form["first_name"]) < 2:
            flash("First name requires 2 or more char","register")
            valid = False
        if len(form["last_name"]) < 2:
            flash("Last name requires 2 or more char", "register")
            valid = False
        if not EMAIL_REGEX.match(form["email"]):
            flash("Invalid email address", "register")
            valid = False
        if len(form["password"]) < 8:
            flash("password requires 8 or more char", "register")
            valid = False
        if form["password"] != form["confirm_password"]:
            flash("password don't match","register")
            valid = False
        if found != None:
            flash("Email already taken","register")
            valid = False
        return valid

