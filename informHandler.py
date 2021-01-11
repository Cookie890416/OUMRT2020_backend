def informUser(mongo,userID,userState,messageStatus,eventName,eventID,message=""):
    userInform=mongo.inform_collection.find_one({"user_id":userID})
    if userInform is None:
        userInform={}
        userInform["user_id"]=userID
        if userState == "driver":
            userInform["driver_context"]=[
                {
                    "event_name":eventName,
                    "status":messageStatus,
                    "event_id":eventID,
                    "text":message
                }
            ]
            userInform["passenger_context"]=[]
        else:
            userInform["passenger_context"]=[
                {
                    "event_name":eventName,
                    "status":messageStatus,
                    "event_id":eventID,
                    "text":message
                }
            ]
            userInform["driver_context"]=[]
        mongo.inform_collection.insert_one(userInform)
    else:
        if userState == "driver":
            userInformList=userInform["driver_context"]
            userInformList.append({
                    "event_name":eventName,
                    "status":messageStatus,
                    "event_id":eventID,
                    "text":message
                })
            mongo.inform_collection.update_one({'user_id':userID},{'$set':{"driver_context":userInformList}})
        else:
            userInformList=userInform["passenger_context"]
            userInformList.append({
                    "event_name":eventName,
                    "status":messageStatus,
                    "event_id":eventID,
                    "text":message
                })
            mongo.inform_collection.update_one({'user_id':userID},{'$set':{"passenger_context":userInformList}})