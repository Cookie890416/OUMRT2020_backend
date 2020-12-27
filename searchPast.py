from flask import Blueprint,request,jsonify,abort
from flask_pymongo import PyMongo
from setup import get_db

searchPast = Blueprint("searchPast",__name__)
mongo = get_db()

@searchPast.route('/search-past',methods=['POST'])
def search():
    result=[]
    userID = request.form['user_id']
    userEvent = mongo.past_collection.find({'$or':[{'driver_id':userID},{'passenger_id':userID}]})
    if userEvent is None:
        return jsonify(result)
    for event in userEvent:
        print(event)
        if event['driver_id'] == userID:
            userData = mongo.user_collection.find_one({'user_id':event['passenger_id']})
            userData.pop("_id")
            event['user']=userData
            event.pop("_id")
            finalRequest=event['final_request']
            finalRequest.pop("_id")
            event['final_request']=finalRequest
            result.append(event)
        else:
            userData = mongo.user_collection.find_one({'user_id':event['driver_id']})
            userData.pop("_id")
            event['user']=userData
            event.pop("_id")
            finalRequest=event['final_request']
            finalRequest.pop("_id")
            event['final_request']=finalRequest
            result.append(event)
    return jsonify(result)