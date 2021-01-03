from flask import Blueprint,request,jsonify,abort
from flask_pymongo import PyMongo
from datetime import datetime
from setup import get_db
from informHandler import informUser
from commonOperation import rejectPeople,deleteAlert,deleteReject

deleteEvent = Blueprint("deleteEvent",__name__)
mongo = get_db()

@deleteEvent.route('/delete-event',methods=['POST'])
def delete():
    stuff = request.form
    eventID = stuff['event_id']
    operation = stuff['operation']
    if operation == 'delete':
        requests=mongo.request_collection.find({'event_id':eventID})
        if requests is not None:
            for userRequest in requests:
                userID=userRequest['user_id']
                rejectPeople(userID,eventID)
                deleteAlert(userID,eventID)
                informUser(mongo,userID,"passenger","reject",eventID," The driver has deleted the event you requested.")
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
        #TODO delete reject table
        return jsonify({"status":True,"reason":""})
    elif operation == 'finish':
        dropEvent = mongo.current_collection.find_one({'event_id':eventID})
        deleteAlert(dropEvent['driver_id'],eventID)
        deleteAlert(dropEvent['passenger_id'],eventID)
        informUser(mongo,dropEvent['driver_id'],"driver","finish",eventID,"One of your event is finished, consider giving a rating.")
        informUser(mongo,dropEvent['passenger_id'],"passenger","finish",eventID,"One of your event is finished, consider giving a rating.")
        dropEvent['status']='gray'
        dropEvent.pop('_id')
        dropEvent['is_rated']=0
        mongo.past_collection.insert_one(dropEvent)
        mongo.current_collection.find_one_and_delete({'event_id':eventID})
        #TODO delete reject table
        return jsonify({"status":True,"reason":""})
    else:
        return abort(400, 'Unknown operation')