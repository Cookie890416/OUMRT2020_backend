import os
import json
import uuid
from flask import Flask, request, render_template
from flask_pymongo import pymongo
from flask.json import jsonify
from setup import create_app
from setup import get_db
from createEvent import createEvent
from deleteEvent import deleteEvent
from requestEvent import requestEvent
from searchEvent import searchEvent
from editEvent import editEvent
# app = Flask(__name__)
# app.config["JSON_AS_ASCII"] = False
# CONNECTION_STRING = "mongodb+srv://cookie:E125330273@cluster0.l02pb.mongodb.net/test_project?retryWrites=true&w=majority"
# client = pymongo.MongoClient(CONNECTION_STRING)
# db = client.flask_mongodb_atlas
app = create_app()
db = get_db()
app.config["JSON_AS_ASCII"] = False
app.register_blueprint(createEvent)
app.register_blueprint(deleteEvent)
app.register_blueprint(requestEvent)
app.register_blueprint(searchEvent)
app.register_blueprint(editEvent)

@app.route('/')
def flask_mongodb_atlas():
    return "Welcome to flask demo"

@app.route('/register',methods=['GET', 'POST'])
def post_data():
    if request.method == 'POST':
        bigObject=(request.json)
        authData=bigObject.get('auth')
        data=bigObject.get('user')
        user_id=str(uuid.uuid1())
        data['user_id']=user_id
        rate={}
        rate['score']=0
        rate['times']=0
        data['rate']=rate
        authData['user_id']=user_id
        db.user_collection.insert(data)
        db.auth_collection.insert(authData)
        return"registed"
    else:
        return"what"
     


@app.route('/newPassword',methods=["POST"])
def new_password():
    mail=request.form['mail']
    password=request.form['password']
    db.auth_collection.update(
        {"user_id" : mail},
        {"$set":{
           "password" :password
        }
        },upsert=True)
    ack={}
    


@app.route('/accountExist',methods=["POST"])
def check():
    mail=request.form['mail']
    mailExist = db.auth_collection.find({'mail':mail})
    if (mailExist):
        return True
    else:
        return False
    


@app.route('/modify',methods=["POST"])
def modify_data():
    dic=request.json
    db.user_collection.update(
        {"user_id" : dic.get('user_id')},
        {"$set":{
           "name" :dic.get('name'),
           "phone_num" : dic.get('phone_num'),
           "sex" : dic.get('sex'),
           "weight" :dic.get('weight'),
           "picture_url" : dic.get('picture_url'),
        }
        },upsert=True)
    return"modified"

@app.route('/score',methods=["POST"])
def score_data():
    user_id=request.form['user_id']
    score=request.form['score']
    oriRate = db.user_collection.find_one({'user_id':user_id}).get('rate')
    ratedScore=(oriRate.get('score')*oriRate.get('times')+score)/(int(oriRate.get('times'))+int(1))
    ratedScore=round(ratedScore,1)
    ratedTime=int(oriRate.get('times'))+int(1)
    ratedRate={}
    ratedRate['score']=ratedScore
    ratedRate['times']=ratedTime
    db.user_collection.update(
        {"user_id" : user_id},
        {"$set":{
           "rate":ratedRate
        }
        },upsert=True)
    return"rated"
    
@app.route('/login',methods=["POST"])
def login():
    mail=request.form['mail']
    password=request.form['password']
    if (db.auth_collection.find_one({'mail':mail,'password':password})):
        return (db.auth_collection.find_one({'mail':mail,'password':password}).get('user_id'))
    else:
        return "Fail"

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)