from flask import Blueprint,request,jsonify
from setup import get_db
from flask_pymongo import PyMongo
from datetime import datetime as dt,timedelta
from informHandler import informUser
from commonOperation import rejectPeople,deleteAlert

requestEvent = Blueprint("requestEvent",__name__)
mongo = get_db()

@requestEvent.route('/request',methods=['POST'])
def requestAdd():
    requestObj = request.json
    if  mongo.current_collection.find_one({'event_id':requestObj['event_id']}) is None:
        return jsonify({"isSuccess":False,"reason":"You are requesting a none existing event."})    
    if mongo.request_collection.find_one({'event_id':requestObj['event_id'],"user_id":requestObj['user_id']}) is not None:
        return jsonify({"isSuccess":False,"reason":"You already requested this event."})
    mongo.request_collection.insert_one(requestObj)
    userID = requestObj['user_id']
    formatString = "%Y-%m-%d %H:%M"
    actualTime = dt.strptime(requestObj['actual_time'],formatString)
    startTime = (actualTime-timedelta(minutes=10)).strftime(formatString)
    endTime = (actualTime+timedelta(minutes=10)).strftime(formatString)
    timeInterval=[startTime,endTime]
    driverAlert=mongo.alert_collection.find_one({'user_id':userID})
    if driverAlert is not None:
        blockTime=driverAlert['block_time']
        blockTime.append({"event_id":requestObj['event_id'],"interval":timeInterval})
        mongo.alert_collection.update_one({'user_id':userID},{"$set":{'block_time':blockTime}})
    else:
        alert={'user_id':userID,
               'block_time':[
                {"event_id":requestObj['event_id'],"interval":timeInterval}
               ]}
        mongo.alert_collection.insert_one(alert)
    currentEvent = mongo.current_collection.find_one({'event_id':requestObj['event_id']})
    driverID = currentEvent['driver_id']
    eventName = currentEvent['event_name']
    informUser(mongo,driverID,"driver","request",eventName,requestObj['event_id'],"You have a request for your event.")
    #infrom event driver
    return jsonify({"isSuccess":True,"reason":""})

@requestEvent.route('/accept-request',methods=['POST'])
def requestAccept():
    requestObj = request.form
    eventID= requestObj['event_id']
    userID= requestObj['user_id']
    requests=mongo.request_collection.find_one({'event_id':eventID,"user_id":userID})
    mongo.current_collection.update_one({"event_id":eventID},{"$set":{"final_request":requests,"passenger_id":userID,"status":"green"}})
    mongo.request_collection.delete_one({'event_id':eventID,"user_id":userID})
    userRequest = mongo.request_collection.find({'event_id':eventID})
    currentEvent = mongo.current_collection.find_one({'event_id':eventID})
    for user in userRequest:
        userID=user["user_id"]
        rejectPeople(userID,eventID)
        deleteAlert(userID,eventID)
        informUser(mongo,userID,"passenger","reject",currentEvent['event_name'],eventID,"You have been rejected by one of your requested driver.")
    mongo.request_collection.delete_many({'event_id':eventID})
    driverID=currentEvent['driver_id']
    informUser(mongo,driverID,"driver","accept",currentEvent['event_name'],eventID,"You have a event set with a passenger.")
    informUser(mongo,userID,"passenger","accept",currentEvent['event_name'],eventID,"You have a event set with a driver.")
    formatString = "%Y-%m-%d %H:%M"
    actualTime = requests["actual_time"]
    actualTime = dt.strptime(actualTime,formatString)
    startTime = (actualTime-timedelta(minutes=10)).strftime(formatString)
    endTime = (actualTime+timedelta(minutes=10)).strftime(formatString)
    timeInterval=[startTime,endTime]
    driverAlert=mongo.alert_collection.find_one({'user_id':driverID})
    if driverAlert is not None:
        blockTime=driverAlert['block_time']
        for eventBlockTime in blockTime:
            if eventBlockTime["event_id"]==eventID:
                eventBlockTime["interval"]=timeInterval
                break
        mongo.alert_collection.update_one({'user_id':driverID},{"$set":{"blockTime":blockTime}})        
    else:
        pass
    return jsonify({"isSuccess":True,"reason":""})

@requestEvent.route('/reject-event',methods=['POST'])
def requestReject():
    requestObj = request.form
    eventID= requestObj['event_id']
    userID= requestObj['user_id']
    reason = requestObj['reason']
    rejectPeople(userID,eventID,reason)
    deleteAlert(userID,eventID)
    mongo.request_collection.find_one_and_delete({"event_id":eventID,"user_id":userID})
    currentEvent = mongo.current_collection.find({"event_id":eventID})
    informUser(mongo,userID,"passenger","reject",currentEvent['event_name'],eventID,"You have been rejected by a driver.")
    #inform user
    return jsonify({"isSuccess":True,"reason":""})