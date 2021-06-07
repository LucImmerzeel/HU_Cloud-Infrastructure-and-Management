import pymongo
#import sys
import os

MONGOHOST = os.environ.get("MONGOHOST", None)
MONGOUSER = os.environ.get("MONGOUSER", None)
MONGOPASSWORD = os.environ.get("MONGOPASSWORD", None)

if MONGOUSER == "" or True:
    #mongoclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mongoclient = pymongo.MongoClient("mongodb://{}:27017/".format(MONGOHOST))
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
    ZONES_PATH = os.environ.get("ZONES_PATH", "C:/Users/StudyUser/PycharmProjects/HU_Cloud-Infrastructure-and-Management/dns-server/Zones")
    from check_if_ip import is_valid_ipv4_address
    # print(from_db("userdb", "records", {"FQDN": "Test.LucImmerzeel.nl"}))
    # array = list(all_from_db("userdb", "records", {"FQDN": "Test.LucImmerzeel.nl"}))
    # print(array)

    records = []
    for record in all_from_db("userdb", "records", {}):
        # print(record)
        records.append(record)

    all_ip = {}

    for record in records:
        if not is_valid_ipv4_address(record["IP"]):
            continue

        if not record["FQDN"].find(".") >= 1 or not any(char.isalpha() for char in record["FQDN"]):
            continue
        all_ip[record["FQDN"].lower()] = record["IP"]

    print(all_ip)

    zone_list = []
    for zone in all_ip:
        split_zone = zone.split(".")
        top_zone = []
        subdomains = []
        subsubdomains = []
        subsubsubdomains = []
        check_if_in_zones = []
        for zones in zone_list:
            check_if_in_zones.append(zones[0])
        if split_zone[-2] + "." + split_zone[-1] in check_if_in_zones:
            for every_zone in zone_list:
                if split_zone[-2] + "." + split_zone[-1] in every_zone:
                    top_zone = zone_list[zone_list.index(every_zone)]
                    subdomains = top_zone[1]
            for subsub in subdomains:
                subsubdomains.append(subsub)
            for x in range(-3, len(split_zone)*-1-1, -1):
                temp_list = []
                for x_subsub in subsubdomains:
                    temp_list.append(x_subsub)

                if split_zone[x] in temp_list:
                    continue
                else:
                    subdomains.append([split_zone[x]])
                    print(subsubdomains)
        else:
            top_zone.append(split_zone[-2] + "." + split_zone[-1])
            for x in range(-3, len(split_zone)*-1-1, -1):
                subsubdomains.append(split_zone[x])
                #print(subsubdomains)
            subdomains.append(subsubdomains)
            top_zone.append(subdomains)
            zone_list.append(top_zone)
    print(zone_list)
    print(all_ip)

    #import dnszoneMetAdd

    for zone in zone_list:
        a_records = ""
        # for subdomain in zone[1]:
        #     try:
        #         a_records += f""", {{"name": "{subdomain[0]}", "ttl": 400, "value": "{all_ip[subdomain[0] + "." + zone[0]]}" }} """
        #     except:
        #             continue
        if a_records == "":
            a_records = f""", {{"name": "@", "ttl": 400, "value": "{all_ip[zone[0]]}" }} """

        print(os.path.join(ZONES_PATH, zone[0] + ".zone"))
        print(f""" /{{  "$origin": "{zone[0]}",
                        "$ttl": 3600,

                        "soa": {{
                            "mname": "ns1.{zone[0]}",
                            "rname": "admin.{zone[0]}",
                            "serial": "{{time}}",
                            "refresh": 3600,
                            "retry": 600,
                            "expire": 604800,
                            "minimum": 86400}},

                        "ns": [{{"host": "ns1.{zone[0]}"}}, {{"host": "ns2.{zone[0]}"}}],
                        "a": [{a_records[1:]}]}}""")


#test()
