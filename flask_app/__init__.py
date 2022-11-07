import os
from flask import Flask
from werkzeug.utils import secure_filename



app = Flask(__name__)
app.secret_key = 'secret_key'

