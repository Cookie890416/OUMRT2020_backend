from flask import Flask,request
from flask_pymongo import pymongo
from flask import json
from flask import jsonify
import os
CONNECTION_STRING = "mongodb+srv://cookie:E125330273@cluster0.l02pb.mongodb.net/test_project?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.flask_mongodb_atlas
user_collection = pymongo.collection.Collection(db,'user_collection')
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
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
        x=[]
        if current_event:
            for i in current_event:
                i.pop("_id")
                if i["status"]=="white":
                    j={}
                    all_request_user=[]
                    all_request=[]
                    for j in db.request_collection.find({"event_id": i["event_id"]}):
                        j.pop("_id")
                        all_request.append(j)
                        i['all_request']=all_request
                        for k in db.user_collection.find({"user_id": j["user_id"]}):
                            k.pop("_id")
                            all_request_user.append(k)
                        i['all_request_user']=all_request_user
                    i.update({"reason":None,"final_request":None,"user":None})
                    x.append(i)
                    return jsonify(x)
                if i["status"]=="green":
                    j={}
                    for j in db.request_collection.find({"event_id": i["event_id"]}):
                        j.pop("_id")
                        
                    for k in db.user_collection.find({"user_id": i["passenger_id"]}):
                        k.pop("_id")
                        i['final_request']=j
                        i['user']=k
                    i.update({"all_request":None,"all_request_user":None,"reason":None})
                    x.append(i)
                    return jsonify(x)
    else:
        return 'No user found!'

@app.route('/query_passenger/<string:user_id>')#test
def query_passenger_test(user_id):
    if user_id:
        final_result=[]
        final_status="white"
        if final_status=="white":
            result=[]
            x=[]
            for i in db.request_collection.find({"user_id": user_id}):
                i.pop("_id")
                result.append(i["event_id"])
            for j in db.current_collection.find({"event_id":{"$in": result}}):
                j.pop("_id")
                temp=db.user_collection.find_one({'user_id':j['driver_id']})
                temp.pop('_id')
                j['user']=temp
                temp = db.request_collection.find_one({'user_id':user_id,'event_id':j['event_id']})
                temp.pop('_id')
                j['my_request']=temp
                j.update({"all_request":None,"all_request_user":None,"reason":None})
                x.append(j)
            final_result.extend(x)
        final_status="green"
        if final_status=="green":
            x=[]
            for i in db.current_collection.find({"passenger_id": user_id}):
                i.pop("_id")
                for j in db.user_collection.find({"user_id": user_id}):
                    j.pop("_id")
                    i['user']=j
                i.update({"all_request":None,"all_request_user":None,"reason":None})
                x.append(i)
            final_result.extend(x)
        final_status="red"
        if final_status=="red":
            x=[]
            temp=db.reject_collection.find_one({"user_id": user_id})['rejected_event_list']
            for event in temp:
                eventid=db.current_collection.find_one({"event_id": event['event_id']})
                if eventid is None:
                    continue
                eventid.pop("_id")
                eventid['status']="red"
                eventid['reason']=event['reason']
                driver=eventid["driver_id"]
                user=db.user_collection.find_one({"user_id":driver})
                user.pop('_id')
                eventid['user']=user
                x.append(eventid)
            final_result.extend(x)
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
if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
# if __name__ == '__main__':
#     app.run(port=8000)