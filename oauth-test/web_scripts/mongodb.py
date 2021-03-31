import pymongo
import sys
import os

MONGOHOST = os.environ.get("MONGOHOST", None)
MONGOUSER = os.environ.get("MONGOUSER", None)
MONGOPASSWORD = os.environ.get("MONGOPASSWORD", None)

if MONGOUSER == "" or True:
    #mongoclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mongoclient = pymongo.MongoClient("mongodb://ec2-34-203-31-252.compute-1.amazonaws.com:27017/")
else:
    print("Using Credentials")
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
    # print(from_db("userdb", "records", {"FQDN": "Test.LucImmerzeel.nl"}))
    # array = list(all_from_db("userdb", "records", {"FQDN": "Test.LucImmerzeel.nl"}))
    # print(array)
    print(update_db("userdb", "users", {"_id": str(101864882111593489975)},  {"$pull": {"records": "606243583fc992ef450ffc16"}}))


test()