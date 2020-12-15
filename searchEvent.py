from flask import Flask,Blueprint,jsonify,request
from flask_pymongo import PyMongo
from datetime import datetime as dt
from . import get_db
mongo = get_db()
searchEvent=Blueprint("searchEvent",__name__)

@searchEvent.route('/query-event',methods=['GET'])
def query():
    #user_id(V),driver_name(V),start(V),end(V),time,is_helmet(V),is_free,driver_sex
    db_filter={}
    userID=request.args.get('user_id')
    userSex=mongo.user_collection.find_one({'user_id':userID})['sex']
    if userSex==True:
        userSex=0
    else:
        userSex=1
    userWeight=mongo.user_collection.find_one({'user_id':userID})['weight']
    db_filter['max_weight']={'$gt':userWeight}
    driverList=[]
    name=request.args.get('driver_name')
    if name is not "":
        for driver in mongo.user_collection.find({'name':name}):
            driverList.append(driver['user_id'])
        db_filter['driver_id']={'$in':driverList}
    isHelmet=request.args.get('is_self_helmet')
    if isHelmet== 'true':
        isHelmet=True
    else:
        isHelmet=False
    is_free=request.args.get('is_free')
    db_filter['is_self_helmet']=isHelmet
    db_filter['acceptable_start_point']=request.args.get('start')
    db_filter['acceptable_end_point']=request.args.get('end')
    db_filter['status']='white'
    if is_free == 'true':
        db_filter['price']=0
    db_filter['acceptable_sex']={'$in':[userSex,2]}
    rejectEventID=[]
    rejectUser=mongo.reject_collection.find_one({'user_id':userID})
    if rejectUser is not None:
        rejectEventList = rejectUser['rejected_event_list']
        for rejectEvent in rejectEventList:
            rejectEventID.append(rejectEvent['event_id'])
        db_filter['event_id'] ={'$nin':rejectEventID}
    print(db_filter)
    match = mongo.current_collection.find(db_filter)
    result=[]
    for eventCandidate in match:
        print(eventCandidate)
        driverSex=mongo.user_collection.find_one({'user_id':eventCandidate['driver_id']})['sex']
        userSexNeed=request.args.get('driver_sex')
        if userSexNeed == "1" and driverSex==True:
            continue
        elif userSexNeed == "0" and driverSex==False:
            continue
        print("HEY I WAS HERE")
        timeInterval = eventCandidate['acceptable_time_interval']
        formatString = "%Y-%m-%d %H:%M"
        startTime = dt.strptime(timeInterval[0],formatString)
        endTime = dt.strptime(timeInterval[1],formatString)
        userTime = dt.strptime(request.args.get('time'),formatString)
        print(startTime,endTime,userTime)
        if userTime < startTime or userTime > endTime:
            print("I WAS CONTINUED")
            continue
        print("HEY I WAS HERE TOO")
        eventCandidate.pop('_id')
        eventObj = eventCandidate
        driverTemp = mongo.user_collection.find_one({'user_id':eventCandidate['driver_id']})
        driverTemp.pop('_id')
        eventObj['user']=driverTemp
        result.append(eventObj)
    return jsonify(result)
        
         
            
            
#TODO 1. find all user_id with that driver_name
#TODO 2. match time with event time interval
#TODO 3. check driver_sex with driver actual sex , check event prefer sex with user actual sex
#TODO 4. check is_free with event price
#TODO 5. match start,driver_id,end,is_helmet
#TODO 6. match weight with user weight

    