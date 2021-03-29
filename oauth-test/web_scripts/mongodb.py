import pymongo
import sys
import os

MONGOHOST = os.environ.get("MONGOHOST", None)
MONGOUSER = os.environ.get("MONGOUSER", None)
MONGOPASSWORD = os.environ.get("MONGOPASSWORD", None)

if MONGOHOST == "localhost":
    mongoclient = pymongo.MongoClient("mongodb://localhost:27017/")
else:
    mongoclient = pymongo.MongoClient("mongodb://{}:{}@{}:27017/".format(MONGOUSER, MONGOPASSWORD, MONGOHOST))


def to_db(database, colomn, list):
    mongodb = mongoclient[database]
    mongocol = mongodb[colomn]
    return mongocol.insert_one(list)


def from_db(database, colomn, list):
    mongodb = mongoclient[database]
    mongocol = mongodb[colomn]
    return mongocol.find_one(list)


def all_from_db(database, colomn, list):
    mongodb = mongoclient[database]
    mongocol = mongodb[colomn]
    return mongocol.find(list)


def replace_db(database, colomn, existinglist, newlist):
    mongodb = mongoclient[database]
    mongocol = mongodb[colomn]
    return mongocol.find_one_and_replace(existinglist, newlist)


def update_db(database, colomn, existinglist, newlist):
    mongodb = mongoclient[database]
    mongocol = mongodb[colomn]
    return mongocol.update_one(existinglist, newlist)


def remove_db(database, colomn, list):
    mongodb = mongoclient[database]
    mongocol = mongodb[colomn]
    return mongocol.delete_one(list)


def test():
    from bson.objectid import ObjectId
    record_ids = None
    records = []

    unique_id = 1
    email = "no@google.com"
    picture = "https://it-immerzeel.nl"
    record_ids = None
    records = []
    try:
        record_ids = from_db("userdb", "users", {"_id": str(101864882111593489975)})["records"]
        if type(record_ids) is str:
            print(record_ids)
            records.append(from_db("userdb", "records", {"_id": ObjectId(record_ids)}))
            print(records)
        else:
            for record_id in record_ids:
                records = from_db("userdb", "records", {"_id": record_id})
    except:
        pass
    print(records)
    if records is not None:
        for record in records:
            print(record)


test()