from setup import get_db

mongo = get_db()

def rejectPeople(userID,eventID,reason="Others are picked,not you."):
    userRejectList=mongo.reject_collection.find_one({'user_id':userID})
    if userRejectList is None:
        mongo.reject_collection.insert_one({'user_id':userID,"rejected_event_list":[{"event_id":eventID,"reason":reason}]})
    else:
        rejectEventList=userRejectList["rejected_event_list"]
        for rejectEvent in rejectEventList:
            if rejectEvent["event_id"]==eventID:
                return
        rejectEventList.append({'event_id':eventID,"reason":reason})
        mongo.reject_collection.update_one({'user_id':userID},{'$set':{'rejected_event_list':rejectEventList}})
    return

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
