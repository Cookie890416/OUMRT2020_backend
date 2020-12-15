from flask import Blueprint,request,jsonify,abort
from flask_pymongo import PyMongo
from . import get_db

deleteEvent = Blueprint("deleteEvent",__name__)
mongo = get_db()

def deleteAlert(userID,eventID):
    userAlertList=mongo.alert_collection.find_one({'user_id':userID})['block_time']
    for i in range(len(userAlertList)):
        if userAlertList[i]['event_id']==eventID:
            userAlertList.pop(i)
            break
    mongo.alert_collection.update_one({'user_id':userID},{'$set':{'block_time':userAlertList}})

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
        mongo.current_collection.find_one_and_delete({'event_id':eventID})
        #TODO notify driver and passenger
        #TODO move to passEvent and status "RED"
        #TODO delete reject table
        return jsonify({"status":True,"reason":""})
    elif operation == 'finish':
        dropEvent = mongo.current_collection.find_one({'event_id':eventID})
        deleteAlert(dropEvent['driver_id'],eventID)
        deleteAlert(dropEvent['passenger_id'],eventID)
        mongo.current_collection.find_one_and_delete({'event_id':eventID})
        #TODO notify driver and passenger
        #TODO move to passEvent and status "GREY"
                #TODO delete reject table
        return jsonify({"status":True,"reason":""})
    else:
        return abort(400, 'Unknown operation')