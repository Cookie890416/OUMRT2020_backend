from flask import Flask,request
from flask_pymongo import pymongo
app = Flask(__name__)
CONNECTION_STRING = "mongodb://localhost:27017/flask_mongodb_atlas"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.flask_mongodb_atlas
def get_db():
    return db

def create_app():
    return app