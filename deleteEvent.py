from flask import Blueprint,request,jsonify,abort
from flask_pymongo import PyMongo
from setup import get_db
from informHandler import informUser
from commonOperation import rejectPeople,deleteAlert,deleteReject
from datetime import datetime as dt,timedelta,date
import uuid

deleteEvent = Blueprint("deleteEvent",__name__)
mongo = get_db()

@deleteEvent.route('/delete-event',methods=['POST'])
def delete():
    stuff = request.form
    eventID = stuff['event_id']
    operation = stuff['operation']
    if operation == 'delete':
        requests=mongo.request_collection.find({'event_id':eventID})
        dropEvent = mongo.current_collection.find_one({'event_id':eventID})
        if requests is not None:
            for userRequest in requests:
                userID=userRequest['user_id']
                rejectPeople(userID,eventID)
                deleteAlert(userID,eventID)
                informUser(mongo,userID,"passenger","reject",dropEvent['event_name'],eventID," The driver has deleted the event you requested.")
        deleteAlert(dropEvent['driver_id'],eventID)
        mongo.current_collection.find_one_and_delete({'event_id':eventID})
        return jsonify({"isSuccess":True,"reason":""})
    elif operation == 'drop':
        dropEvent = mongo.current_collection.find_one({'event_id':eventID})
        deleteAlert(dropEvent['driver_id'],eventID)
        deleteAlert(dropEvent['passenger_id'],eventID)
        informUser(mongo,dropEvent['driver_id'],"driver","drop",dropEvent['event_name'],eventID,"One of your event is being dropped.")
        informUser(mongo,dropEvent['passenger_id'],"passenger","drop",dropEvent['event_name'],eventID,"One of your event is being dropped.")
        dropEvent['status']='red'
        dropEvent.pop('_id')
        dropEvent['is_rated']=0
        mongo.past_collection.insert_one(dropEvent)
        mongo.current_collection.find_one_and_delete({'event_id':eventID})
        #TODO delete reject table
        return jsonify({"isSuccess":True,"reason":""})
    elif operation == 'finish':
        dropEvent = mongo.current_collection.find_one({'event_id':eventID})
        deleteAlert(dropEvent['driver_id'],eventID)
        deleteAlert(dropEvent['passenger_id'],eventID)
        informUser(mongo,dropEvent['driver_id'],"driver","finish",dropEvent['event_name'],eventID,"One of your event is finished, consider giving a rating.")
        informUser(mongo,dropEvent['passenger_id'],"passenger","finish",dropEvent['event_name'],eventID,"One of your event is finished, consider giving a rating.")
        dropEvent['status']='gray'
        dropEvent.pop('_id')
        dropEvent['is_rated']=0
        mongo.past_collection.insert_one(dropEvent)
        #check repeat and add back
        if any(dropEvent['repeat']):     
            dropEvent.pop('is_rated')
            dropEvent.pop('passenger_id')
            dropEvent.pop('final_request')
            dropEvent['status']='white'
            dropEvent['event_id']=str(uuid.uuid4())
            timeInterval=dropEvent['acceptable_time_interval']
            formatString = "%Y-%m-%d %H:%M"
            today = date.today().weekday()
            repeat=dropEvent['repeat']
            i=(today+1)%7
            #find next 'true'
            while i!=today:
                if repeat[i]:
                    break
                i=(i+1)%7
            if i == today:
                i = 7
            else:
                i = ((i-today)%7)
            nextTime=date.today()+timedelta(days=i)
            startTime = dt.strptime(timeInterval[0],formatString)
            endTime = dt.strptime(timeInterval[1],formatString)
            duration = nextTime - startTime.date()
            startTime = startTime+duration
            endTime = endTime+duration
            dropEvent['acceptable_time_interval'][0]=startTime.strftime(formatString)
            dropEvent['acceptable_time_interval'][1]=endTime.strftime(formatString)
            mongo.current_collection.insert_one(dropEvent)
        mongo.current_collection.find_one_and_delete({'event_id':eventID})
        #TODO delete reject table
        return jsonify({"isSuccess":True,"reason":""})
    else:
        return abort(400, 'Unknown operation')