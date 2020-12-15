from flask import Flask,request
from flask_pymongo import pymongo
app = Flask(__name__)
CONNECTION_STRING = "mongodb+srv://cookie:E125330273@cluster0.l02pb.mongodb.net/test_project?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.flask_mongodb_atlas
def get_db():
    return db

def create_app():
    return app