from flask import Flask,jsonify
from flask_pymongo import pymongo
import json
import os
CONNECTION_STRING = "mongodb+srv://cookie:E125330273@cluster0.l02pb.mongodb.net/test_project?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.flask_mongodb_atlas
user_collection = pymongo.collection.Collection(db, 'user_collection')
app = Flask(__name__)
@app.route('/')
def flask_mongodb_atlas():
    return "flask mongodb atlas!"
@app.route('/query/<string:name>')
def query_user(name):
    if name:
        users = db.user.find({'name': name})
        x=[]
        if users:
            for i in users:
                i.pop("_id")
                x.append(i)
            return jsonify(x)
    else:
        return 'No user found!'
#test to insert data to the data base
@app.route("/test")
def test():
    db.user.insert_one({"name": "John"})
    return "Connected to the data base!"
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
# if __name__ == '__main__':
#     app.run(port=8000)