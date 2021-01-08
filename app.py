from flask import Flask,request
from flask_pymongo import pymongo
from flask import jsonify
import os
from datetime import datetime as dt
from setup import create_app
from setup import get_db
from createEvent import createEvent
from deleteEvent import deleteEvent
from requestEvent import requestEvent
from searchEvent import searchEvent
from editEvent import editEvent
from searchPast import searchPast
from getInform import getInform
# 岳均
import json
import uuid
# CONNECTION_STRING = "mongodb+srv://cookie:E125330273@cluster0.l02pb.mongodb.net/test_project?retryWrites=true&w=majority"
# client = pymongo.MongoClient(CONNECTION_STRING)
# db = client.flask_mongodb_atlas
# app = Flask(__name__)
app = create_app()
db = get_db()
app.config["JSON_AS_ASCII"] = False

app.register_blueprint(createEvent)
app.register_blueprint(deleteEvent)
app.register_blueprint(requestEvent)
app.register_blueprint(searchEvent)
app.register_blueprint(editEvent)
app.register_blueprint(searchPast)
app.register_blueprint(getInform)

@app.route('/')
def flask_mongodb_atlas():
    return "flask mongodb atlas!"
@app.route('/test-field',methods=['POST'])
def showField():
    data = request.form
    return  data['user']
@app.route('/query_driver/<string:driver_id>')
def query_driverevent(driver_id):
    if driver_id:
        current_event = db.current_collection.find({"driver_id": driver_id})
        final_result=[]
        if current_event:
            for i in current_event:
                i.pop("_id")
                if i["status"]=="white":
                    x=[]
                    all_request_user=[]
                    all_request=[]
                    for j in db.request_collection.find({"event_id": i["event_id"]}):
                        j.pop("_id")
                        all_request.append(j)
                        # i['all_request']=all_request
                        for k in db.user_collection.find({"user_id": j["user_id"]}):
                            k.pop("_id")
                            all_request_user.append(k)
                        # i['all_request_user']=all_request_user
                    i.update({"all_request_user":all_request_user,"all_request":all_request,"reason":None,"user":None,"my_request":None})
                    x.append(i)
                    final_result.extend(x)
                if i["status"]=="green":
                    x=[]
                    trash2=i["final_request"]
                    trash2.pop("_id")
                    for k in db.user_collection.find({"user_id": i["passenger_id"]}):
                        k.pop("_id")
                        i['user']=k
                    i.update({"final_request":trash2,"all_request":[],"all_request_user":[],"reason":None,"my_request":None})
                    x.append(i)
                    final_result.extend(x)
                
            return jsonify(final_result)
    else:
        return 'No user found!'
@app.route('/query_passenger/<string:user_id>')#test
def query_passenger_test(user_id):
    if user_id:
        final_result=[]
        final_status="white"
        if final_status=="white":
            print("white")
            result=[]
            x=[]
            for i in db.request_collection.find({"user_id": user_id}):
                print("request find")
                i.pop("_id")
                result.append(i["event_id"])
            for j in db.current_collection.find({"event_id":{"$in": result}}):
                j.pop("_id")
                temp1=db.user_collection.find_one({'user_id':j['driver_id']})
                temp1.pop('_id')
                j['user']=temp1
                temp1 = db.request_collection.find_one({'user_id':user_id,'event_id':j['event_id']})
                temp1.pop('_id')
                j['my_request']=temp1
                j.update({"all_request":[],"all_request_user":[],"reason":None})
                x.append(j)
            final_result.extend(x)
        final_status="green"
        if final_status=="green":
            print("green")
            x=[]
            for i in db.current_collection.find({"passenger_id": user_id}):
                i.pop("_id")
                trash=i["final_request"]
                trash.pop("_id")
                for j in db.user_collection.find({"user_id": i["driver_id"]}):
                    j.pop("_id")
                    i['user']=j
                i.update({"final_request":trash,"all_request":[],"all_request_user":[],"reason":None,"my_request":None})
                x.append(i)
            final_result.extend(x)
        final_status="red"
        if final_status=="red":
            print("red")
            x=[]
            if db.reject_collection.find_one({"user_id": user_id})!=None:
                temp1=db.reject_collection.find_one({"user_id": user_id})['rejected_event_list']
                print("REJECT FIND")
                for event in temp1:
                    eventid=db.current_collection.find_one({"event_id": event['event_id']})
                    if eventid is None:
                        print("event none")
                        continue
                    eventid.pop("_id")
                    eventid['status']="red"
                    eventid['reason']=event['reason']
                    driver=eventid["driver_id"]
                    user=db.user_collection.find_one({"user_id":driver})
                    user.pop('_id')
                    eventid['user']=user
                    eventid.update({"all_request":[],"all_request_user":[],"final_request":None,"my_request":None})
                    x.append(eventid)
            
            final_result.extend(x)
        print("HERE")
        print(final_result)
        return jsonify(final_result)
@app.route('/query/<string:event_id>')
def query_user(event_id):
    if event_id:
        users = db.current_collection.find({"event_id": event_id})
        x=[]
        if users:
            for i in users:
                i.pop("_id")
                x.append(i)
            return jsonify(x)
    else:
        return 'No user found!'

@app.route('/alert',methods=['POST'])
def alert_time():
    reason=[]
    temp={}
    user_id=request.form['user_id']
    time=request.form['time']
    time = dt.strptime(time, "%Y-%m-%d %H:%M")
    if db.alert_collection.find_one({"user_id": user_id}):
        temp=db.alert_collection.find_one({'user_id':user_id})["block_time"]
        for i in temp:
            startTime=i["interval"][0]
            endTime=i["interval"][1]
            d_time = dt.strptime(startTime, "%Y-%m-%d %H:%M")
            d_time1 =  dt.strptime(endTime, "%Y-%m-%d %H:%M")
            if time>d_time and time<d_time1:
                eventid=db.current_collection.find_one({"event_id": i["event_id"]})
                eventid.pop("_id")
                # return eventid["event_name"]
                reason.append(eventid["event_name"])#reason=["金瓜石特快車,林森北一日遊,基隆火車站躺著玩"]
                # return jsonify(reason)
        reason=" ".join(reason)
    if len(reason)>0:
        return jsonify({"isSuccess":False,"reason":reason})
    else:
        return jsonify({"isSuccess":True,"reason":""})
@app.route('/alert_Interval',methods=['POST'])
def alert_timeInterval():
    reason=[]
    temp={}
    user_id=request.form['user_id']
    query_TimeStart=request.form['query_TimeStart']
    query_TimeEnd=request.form['query_TimeEnd']
    query_TimeStart = dt.strptime(query_TimeStart, "%Y-%m-%d %H:%M")
    query_TimeEnd = dt.strptime(query_TimeEnd, "%Y-%m-%d %H:%M")
    temp=db.alert_collection.find_one({'user_id':user_id})
    if temp is not None:
        temp=temp["block_time"]
        for i in temp:
            startTime=i["interval"][0]
            endTime=i["interval"][1]
            start = dt.strptime(startTime, "%Y-%m-%d %H:%M")
            end =  dt.strptime(endTime, "%Y-%m-%d %H:%M")
            if (query_TimeStart<start and query_TimeEnd>start) or (query_TimeStart>start and query_TimeStart<end):
                eventid=db.current_collection.find_one({"event_id": i["event_id"]})
                eventid.pop("_id")
                # return eventid["event_name"]
                reason.append(eventid["event_name"])#reason="金瓜石特快車 林森北一日遊 基隆火車站躺著玩"
                # return jsonify(reason)
        reason=" ".join(reason)
    if len(reason)>0:
        return jsonify({"isSuccess":False,"reason":reason})
    else:
        return jsonify({"isSuccess":True,"reason":""})
    
#岳均的
@app.route('/register',methods=['GET', 'POST'])
def post_data():
    if request.method == 'POST':
        bigObject=(request.json)
        authData=bigObject.get('auth')
        data=bigObject.get('user')
        user_id=str(uuid.uuid1())
        data['user_id']=user_id
        rate={}
        rate['score']=0.0
        rate['times']=0
        data['rate']=rate
        authData['user_id']=user_id
        db.user_collection.insert(data)
        db.auth_collection.insert(authData)
        return jsonify({"isSuccess":True,"reason":""})
    else:
        return jsonify({"isSuccess":False,"reason":""})
     


@app.route('/newPassword',methods=["POST"])
def new_password():
    mail=request.form['mail']
    password=request.form['password']
    db.auth_collection.update(
        {"mail" : mail},
        {"$set":{
           "password" :password
        }
        },upsert=True)
    return jsonify({"isSuccess":True,"reason":""})
    


@app.route('/accountExist',methods=["POST"])
def check():
    mail=request.form['mail']
    print (mail)
    mailExist = db.auth_collection.find_one({'mail':mail})
    ack={}
    if (mailExist):
        ack={"isSuccess":True,
        "reason":""}
    else:
        ack={"isSuccess":False,
        "reason":""}
    return ack
    
@app.route('/showData',methods=["POST"])
def show():
    user_id=request.form['user_id']
    x = db.user_collection.find_one({'user_id':user_id})
    x.pop("_id")
    return jsonify(x)

@app.route('/alter-user',methods=["POST"])
def modify_data():
    dic=request.json
    if(dic.get('user_id')):
        db.user_collection.update(
            {"user_id" : dic.get('user_id')},
            {"$set":{
                "name" :dic.get('name'),
                "phone_num" : dic.get('phone_num'),
                "weight" :dic.get('weight'),
                "picture_url" : dic.get('picture_url'),
            }
            },upsert=True)
        ack={"isSuccess":True,
        "reason":""}
    return ack

@app.route('/score',methods=["POST"])
def score_data():
    event_id=request.form['event_id']
    user_id=request.form['user_id']
    score=request.form['score']
    def ratePeople(score):
        oriRate = db.user_collection.find_one({'user_id':user_id}).get('rate')
        ratedScore=(oriRate.get('score')*int(oriRate.get('times'))+float(score))/(float(oriRate.get('times'))+1)
        ratedScore=round(ratedScore,10)
        ratedTime=int(oriRate.get('times'))+int(1)
        ratedRate={}
        ratedRate['score']=ratedScore
        ratedRate['times']=ratedTime
        db.user_collection.update(
        {"user_id" : user_id},
        {"$set":{
           "rate":ratedRate
        }
        },upsert=True)
    unRatedEvent= db.past_collection.find_one({'event_id':event_id})
    if(unRatedEvent.get("passenger_id")==user_id):
        if(unRatedEvent.get("is_rated")%2==0):
            ratePeople(score)
            db.past_collection.update(
            {"event_id" : event_id},
            {"$inc":{
                "is_rated":1
                }
            })
            ack={
                "isSuccess":True,
                "reason":""
            }
        else:
            ack={
                "isSuccess":False,
                "reason":"Overrate"
            }                    
    else:
        if(unRatedEvent.get("is_rated")<2):
            ratePeople(score)
            db.past_collection.update(
            {"event_id" : event_id},
            {"$inc":{
                "is_rated":2
                }
            })
            ack={
                "isSuccess":True,
                "reason":""
                }
        else:
            ack={
                "isSuccess":False,
                "reason":"Overrate"
                }           
    return jsonify(ack)
    
@app.route('/login',methods=["POST"])
def login():
    mail=request.form['mail']
    password=request.form['password']
    if (db.auth_collection.find_one({'mail':mail,'password':password})):
        user_id=db.auth_collection.find_one({'mail':mail,'password':password}).get('user_id')
        x = db.user_collection.find_one({'user_id':user_id})
        x.pop("_id")
        return jsonify(x)
    else:
        return "Fail"
if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get('PORT', 5602))
    app.run(host='0.0.0.0', port=port)
# if __name__ == '__main__':
#     app.run(port=8000)