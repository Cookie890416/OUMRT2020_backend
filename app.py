from flask import Flask,jsonify, request
import pymongo 
from flask_pymongo import PyMongo
import json
from IPython.utils import process
client=pymongo.MongoClient(host='127.0.0.1')
db=client.test
db_list = client.list_database_names()
collections = db.user
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
mongo = PyMongo(app, uri=process.env.MONGODB_URI )

@app.route('/poster/<string:person>')
def post_data(person):
    personobj=json.loads(str(person))
    collections.insert_one(personobj)
    return str(person)

@app.route('/find/<string:name>')
def find_data(name):

    if name:
        users = mongo.db.user.find({'name':name})
        x=[]
        for user in users:
            user.pop("_id")
            x.append(user)
        return jsonify(x)

    
@app.route('/why')
def why():
    return str(db_list)


@app.route('')
def why():
    return "hello VV"
    



@app.route('/hello')
def hello():
    return "hello VV"



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)