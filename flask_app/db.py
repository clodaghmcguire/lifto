import os
from pymongo import MongoClient


DB_HOST = os.getenv('DB_HOST', 'localhost')
client = MongoClient(host=DB_HOST, port=27017)
db = client.flask_db
lifto = db.lifto
tokens = db.tokens