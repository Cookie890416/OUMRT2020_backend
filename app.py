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
    return request.data
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
                if i["status"]=="red":
                    for j in db.request_collection.find({"event_id": i["event_id"]}):
                        for k in db.reject_collection.find({"user_id": j["user_id"]}):
                            k.pop("_id")
                            k.pop("user_id")
                            r=k.get("rejected_event_list")
                            for s in r:
                                if s.get("event_id")==i["event_id"]:
                                    i['reason']=s["reason"]
                    i.update({"all_request":None,"all_request_user":None})
                    i.update({"final_request":None,"user":None})
                    x.append(i)
                    return jsonify(x)
    else:
        return 'No user found!'
@app.route('/query_passenger/<string:passenger_id>')#乘客綠
def query_passenger_green(passenger_id):
    if passenger_id:
        current_event = db.current_collection.find({"passenger_id": passenger_id})
        x=[]
        if current_event:
            for i in current_event:
                i.pop("_id")
                if i["status"]=="white":
                    for j in db.user_collection.find({"user_id": i["driver_id"]}):
                        j.pop("_id")
                    i['user']=j
                    i.update({"all_request":None,"all_request_user":None,"reason":None})
                    x.append(i)
                    return jsonify(x)
                if i["status"]=="green":
                    for j in db.user_collection.find({"user_id": i["driver_id"]}):
                        j.pop("_id")
                    i['user']=j
                    i.update({"all_request":None,"all_request_user":None,"reason":None})
                    x.append(i)
                    return jsonify(x)
                # if i["status"]=="red":
                #     for j in db.user_collection.find({"user_id": i["driver_id"]}):
                #         j.pop("_id")
                #     i['user']=j
                #     i.update({"all_request":None,"all_request_user":None,"reason":None})
                #     x.append(i)
                #     return jsonify(x)
    else:
        return 'No user found!'
@app.route('/query_passenger/<string:user_id>')#乘客白
def query_passenger_white(user_id):
    if user_id:
        x=[]
        for i in db.request_collection.find({"user_id": user_id}):
            i.pop("_id")
            for j in db.current_collection.find({"event_id": i["event_id"]}):
                j.pop("_id")
                if j["status"]=="white":
                    for k in db.reject_collection.find({"user_id": j["user_id"]}):
                        k.pop("_id")
                        if k!=None:
                            j["status"]="red"
                            k.pop("user_id")
                            r=k.get("rejected_event_list")
                            for s in r:
                                if s.get("event_id")==i["event_id"]:
                                    i['reason']=s["reason"]
                j.update({"all_request":None,"all_request_user":None})
                j.update({"final_request":None,"user":None})
            x.append(j)
        return jsonify(x)
    else:
        return 'No user found!'
@app.route('/query_passenger/<string:passenger_id>')#乘客紅
def query_passenger_red(passenger_id):
    if passenger_id:
        x=[]
        for i in db.current_collection.find({"passenger_id": passenger_id}):
            i.pop("_id")
            if i["status"]=="red":
                for j in db.request_collection.find({"event_id": i["event_id"]}):
                    for k in db.reject_collection.find({"user_id": j["user_id"]}):
                        k.pop("_id")
                        k.pop("user_id")
                        r=k.get("rejected_event_list")
                        for s in r:
                            if s.get("event_id")==i["event_id"]:
                                i['reason']=s["reason"]
                i.update({"all_request":None,"all_request_user":None})
                i.update({"final_request":None,"user":None})
                x.append(i)
                return jsonify(x)
    else:
        return 'No user found!'

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
#test to insert data to the data base
@app.route("/insert")
def test():
    db.current_collection.insert_one({"event_id": "001",
  "event_name":"金瓜石特快車",
  "status": "green",
  "driver_id": "ABC",
  "passenger_id": "XYZ",
  "acceptble_time_interval": ["2020/10/16 13:00", "2020/10/16 15:00"],
  "acceptble_start_point": ["海大校門口","新豐街","祥豐街"],
  "acceptble_end_point": ["九份金瓜石","九份老街","金瓜石博物館"],
  "acceptable_sex": true,
  "max_weight": 100,
  "price": 50,
  "is_self_helmet": true,
  "repeat": [true, true, true, true, true, true, true],

  "actual_time": "2020/10/16 13:30",
  "actual_start_point":"海大校門口",
  "actual_end_point":"九份老街",
  "extra_needed": "山路請慢慢騎"})
    return "Insert success"
@app.route('/delete/<string:event_id>')
def delete_docs(event_id):
    db.current_collection.remove({"event_id":event_id})
    return "Delete success"
@app.route('/update/<string:event_id>')
def update_docs(event_id):
    db.current_collection.update(
        {"event_id" : event_id},
        {"$set":
            {"status": "red"}
        },upsert=True)
    return "Update success"
if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
# if __name__ == '__main__':
#     app.run(port=8000)