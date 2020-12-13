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
@app.route('/query_driver/<string:driver_id>')
def query_event(driver_id):
    if driver_id:
        current_event = db.current_collection.find({"driver_id": driver_id})
        x=[]
        if current_event:
            for i in current_event:
                i.pop("_id")
                # a_dictionary=i
                
                if i["status"]=="white":
                    j={}
                    for j in db.request_collection.find({"event_id": i["event_id"]}):
                        j.pop("_id")
                        # b_dictionary=j
                        # final_dictionary = {**a_dictionary, **b_dictionary}
                    for s in db.request_collection.find({"event_id": i["event_id"]}):
                        for k in db.user_collection.find({"user_id": s["user_id"]}):
                            k.pop("_id")
                            # c_dictionary=k
                            # final_dictionary = {**final_dictionary, **c_dictionary}
                            i['all_request_user']=k
                            i['all_request']=j
                    
                    # d_dictionary={"reason":[],"final_request":[],"user":[]}
                    i.update({"reason":None,"final_request":None,"user":None})
                    x.append(i)
                    # final_dictionary = {**final_dictionary, **d_dictionary}
                    # x.append(final_dictionary)
                    return jsonify(x)
                if i["status"]=="green":
                    x.append({"all_request":[],"all_request_user":[],"reason":[]})
                    for j in db.request_collection.find({"event_id": i["event_id"]}):
                        j.pop("_id")
                        x.append(j)
                    
                    for j in db.user_collection.find({"user_id": i["passenger_id"]}):
                        j.pop("_id")
                        x.append(j)
                    
                    return jsonify(x)
                if i["status"]=="red":
                    x.append({"all_request":[],"all_request_user":[]})
                    
                    for j in db.request_collection.find({"event_id": i["event_id"]}):
                        for k in db.reject_collection.find({"user_id": j["user_id"]}):

                            k.pop("_id")
                            k.pop("user_id")
                            r=k.get("rejected_event_list")
                            for s in r:
                                if s.get("event_id")=="002":
                                    x.append(s)

                    x.append({"final_request":[],"user":[]})
                    return jsonify(x)
    else:
        return 'No user found!'
# @app.route('/query_user/<string:user_id>/<string:status>')
# def query_event(user_id):
#     if user_id:
#         current_event = db.user_collection.find({"user_id": user_id})
#         status=db.current_collection.find({"status": i["status"]})
#         x=[]
#         if current_event and status:
#             for i in current_event:
#                 i.pop("_id")
#                 x.append(i)
#                 if i["status"]=="white":
#                     for j in db.request_collection.find({"user_id": i["user_id"]}):
#                         j.pop("_id")
#                         x.append(j)
#                 return jsonify(x)
# @app.route('/query/<string:event_id>')
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