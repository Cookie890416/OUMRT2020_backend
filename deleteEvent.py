from flask import Blueprint,request,jsonify,abort
from flask_pymongo import PyMongo
from datetime import datetime
from setup import get_db
from informHandler import informUser

deleteEvent = Blueprint("deleteEvent",__name__)
mongo = get_db()

def deleteAlert(userID,eventID):
    userAlertList=mongo.alert_collection.find_one({'user_id':userID})['block_time']
    for i in range(len(userAlertList)):
        if userAlertList[i]['event_id']==eventID:
            userAlertList.pop(i)
            break
    mongo.alert_collection.update_one({'user_id':userID},{'$set':{'block_time':userAlertList}})

def deleteReject(userID,eventID):
    userReject = mongo.reject_collection.find_one({'user_id':userID})
    if userReject is None:
        return
    userRejectList = userReject["rejected_event_list"]
    for i in range(len(userRejectList)):
        if userRejectList[i]['event_id'] == eventID:
            userRejectList.pop(i)
            break
    mongo.reject_collection.update_one({'user_id':userID},{'$set':{"rejected_event_list":userRejectList}})

@deleteEvent.route('/delete-event',methods=['POST'])
def delete():
    stuff = request.form
    eventID = stuff['event_id']
    operation = stuff['operation']
    if operation == 'delete':
        requests=mongo.request_collection.find_one({'event_id':eventID})
        if requests is not None:
            return jsonify({"isSuccess":False,"reason":"You have a request for this event. Please reply first."}) 
        else:
            dropEvent = mongo.current_collection.find_one({'event_id':eventID})
            deleteAlert(dropEvent['driver_id'],eventID)
            mongo.current_collection.find_one_and_delete({'event_id':eventID})
        return jsonify({"status":True,"reason":""})
    elif operation == 'drop':
        dropEvent = mongo.current_collection.find_one({'event_id':eventID})
        deleteAlert(dropEvent['driver_id'],eventID)
        deleteAlert(dropEvent['passenger_id'],eventID)
        informUser(mongo,dropEvent['driver_id'],"driver","drop",eventID,"One of your event is being dropped.")
        informUser(mongo,dropEvent['passenger_id'],"passenger","drop",eventID,"One of your event is being dropped.")
        dropEvent['status']='red'
        dropEvent.pop('_id')
        dropEvent['is_rated']=0
        mongo.past_collection.insert_one(dropEvent)
        mongo.current_collection.find_one_and_delete({'event_id':eventID})
        #notify driver and passenger
        #TODO delete reject table
        return jsonify({"status":True,"reason":""})
    elif operation == 'finish':
        dropEvent = mongo.current_collection.find_one({'event_id':eventID})
        deleteAlert(dropEvent['driver_id'],eventID)
        deleteAlert(dropEvent['passenger_id'],eventID)
        informUser(mongo,dropEvent['driver_id'],"driver","finish",eventID,"One of your event is finished, consider giving a rating.")
        informUser(mongo,dropEvent['passenger_id'],"passenger","finish",eventID,"One of your event is finished, consider giving a rating.")
        dropEvent['status']='grey'
        dropEvent.pop('_id')
        dropEvent['is_rated']=0
        mongo.past_collection.insert_one(dropEvent)
        mongo.current_collection.find_one_and_delete({'event_id':eventID})
        #notify driver and passenger
        #TODO delete reject table
        return jsonify({"status":True,"reason":""})
    else:
        return abort(400, 'Unknown operation')