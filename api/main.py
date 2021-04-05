from flask import Flask, request, jsonify, json
from flask_pymongo import PyMongo
from marshmallow import Schema, fields, ValidationError
from bson.json_util import dumps
from json import loads

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://kurtp:thislab3@cluster0.wn7il.mongodb.net/week3lab3?retryWrites=true&w=majority"
mongo = PyMongo(app)

UserProfile = {
    "success": True,
    "data": {
        "last_updated": "",
        "username": "Hannibal",
        "role": "Engineer",
        "color": "yellow"
    }
}


class TankSchema(Schema):
    location = fields.String(required=True)
    lat = fields.String(required=True)
    long = fields.String(required=True)
    percentage_full = fields.Integer(required=True)


class Level(Schema):
    tank_id = fields.Integer(required=True)
    percentage_full = fields.Integer(required=True)


@app.route("/")
def home():
    return "ECSELAB6"


@app.route("/profile", methods=["GET", "POST", "Patch"])
def get_profile():
    if request.method == "GET":
        return jsonify(UserProfile)

        if request.method == "POST":
            UserProfile["data"]["username"] = (request.json["username"])
            UserProfile["data"]["role"] = (request.json["role"])
            UserProfile["data"]["color"] = (request.json["color"])
            UserProfile["data"]["last_updated"] = datetime.now()

            return jsonify(UserProfile)

            if request.method == "PATCH":

                tempDict = request.json
                tempDict["last_updated"] = datetime.now()
                attributes = tempDict.keys()

            for attribute in attributes:
                UserProfile["data"][attribute] = tempDict[attribute]

    return jsonify(UserProfile)


@app.route("/data")
def get_tanks():
    tanks = mongo.db.Tanks.find()
    return jsonify(loads(dumps(tanks)))


@app.route("/data", methods=["POST"])
def add_Tanks():
    try:
        newtank = TankSchema().load(request.json)
        tank_id = mongo.db.Tanks.insert_one(newtank).inserted_id
        tank = mongo.db.Tanks.find_one(tank_id)

        return jsonify(loads(dumps(newtank)))
    except ValidationError as VE:
        return VE.messages, 400


@app.route("/data/<ObjectId:id>", methods=["PATCH"])
def update_tank(id):
    mongo.db.Tanks.update_one({"_id": id}, {"$set": request.json})
    tank = mongo.db.Tanks.find_one(id)
    return loads(dumps(tank))


@app.route("/data/<ObjectId:id>", methods=["DELETE"])
def delete_tank(id):
    result = mongo.db.Tanks.delete_one({"_id": id})

    if result.deleted_count == 1:
        return{"success": True}
        # else:
        return{"success": False}, 400


def map(x, Low_in, High_in, Low_out, High_out):
    return int((x - Low_in) * (High_out - Low_out))/((High_in - Low_in) + Low_out)


@app.route("/tank", methods=["POST"])
def tank_data():
    try:
        tank_id = request.json["tank_id"]
        water_level = request.json["water_level"]
        percentage_full = map(water_level, 200, 10, 0, 100)

        jsonBody = {
            "tank_id": tank_id,
            "percentage_full": percentage_full
        }

        tank_level = Level().load(jsonBody)
        mongo.db.levels.insert_one(tank_level)

        now = datetime.now()
        dt = now.strftime("%d/%m/%Y %H:%M:%S")

        return {
            "success": True,
            "msg": "saved data",
            "date": dt
        }
    except ValidationError as e:
        return e.messages, 400


if __name__ == "__main__":
    app.run(debug=True,
            host="192.168.0.9",
            port=5000
            )
