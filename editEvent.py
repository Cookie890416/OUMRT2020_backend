from flask import Blueprint,request,jsonify,abort
from setup import get_db
from flask_pymongo import PyMongo

mongo = get_db()
editEvent = Blueprint("editEvent",__name__)

@editEvent.route("/alter-event",methods=['POST'])
def edit():
    data=request_collection.json
    eventID=data['event_id']
    if mongo.current_collection.find_one({"event_id":eventID}) is None:
        abort(400,"Event not found")
    request_collections = mongo.request_collection.find_one({"event_id":eventID})
    eventStatus = mongo.current_collection.find_one({"event_id":eventID})['status']
    if eventStatus == "green":
        return jsonify({"isSuccess":False,'reason':"You cannot edit this event,it is set."})
    if request_collections is not None:
        return jsonify({'isSuccess':False,'reason':'You have a request_collection for this event. Please reply first.'})
    else:
        data.pop('event_id')
        for stuff in data:
            if stuff == 'acceptable_time_interval':
                userID=mongo.current_collection.find_one({'event_id':eventID})['driver_id']
                userAlert=mongo.alert_collection.find_one({'user_id':userID})
                alertTime=userAlert['block_time']
                for time in alertTime:
                    if time['event_id']==eventID:
                        time['interval']=data['acceptable_time_interval']
                        break
                mongo.alert_collection.update_one({'user_id':userID},{"$set":{'block_time':alertTime}})
            mongo.current_collection.update_one({"event_id":eventID},{"$set":{stuff:data[stuff]}})
    return jsonify({"isSuccess":True,"reason":""})               
    