from flask import Blueprint,request,jsonify
from setup import get_db
from flask_pymongo import PyMongo

getInform = Blueprint("getInform",__name__)
mongo = get_db()

@getInform.route('/get-inform',methods=['POST'])
def getUserInform():
    requestObj = request.form
    userID = requestObj['user_id']
    userInform = mongo.inform_collection.find_one({"user_id":userID})
    if userInform is None:
        result = {"driver_context":[],"passenger_context":[]}
    else:
        result = {"driver_context":userInform['driver_context'],"passenger_context":userInform['passenger_context']}
    return jsonify(result)
