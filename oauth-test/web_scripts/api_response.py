import json
from .mongodb import from_db, all_from_db, to_db, update_db
from flask import request
from flask_login import current_user
from bson.objectid import ObjectId
from datetime import datetime
from .check_if_ip import is_valid_ipv4_address
#from .dns_records import add_dns_record
import os

#from dnszoneMetAdd import DnsZone


def api_response():
    token = request.args.get('token')
    user_id = current_user.id
    return f"<p>Your ID is {user_id}</p>"


def api_update():
    # from_db()
    # user = User(
    #     id_=user_info["id"], name=user_info["name"], email=user_info["email"],
    #     profile_pic=str(user_info.get('avatar_url'))
    # )

    fqdn = request.args.get('fqdn')
    ip = request.args.get('ip')

    if not is_valid_ipv4_address(ip):
        return f"The IP is not valid, because '{ip}' is not a valid IP."

    if not fqdn.find(".") >= 1:
        return f"The FQDN is not valid, because '{fqdn}' is not a valid FQDN."

    record_ids = None
    records = []
    record_ids = from_db("userdb", "users", {"_id": str(current_user.id)})["records"]

    try:
        #record_ids = from_db("userdb", "users", {"_id": str(current_user.id)})["records"]
        if type(record_ids) is str:
            records.append(from_db("userdb", "records", {"_id": ObjectId(record_ids)}))
        else:
            for record_id in record_ids:
                records.append(from_db("userdb", "records", {"_id": ObjectId(record_id)}))
    except:
        pass

    all_fqdn = {}
    all_ip = {}
    if records is not None and records is not []:
        # return str(records)
        for record in records:
            all_fqdn[record["FQDN"]] = record["date_time"]
            all_ip[record["FQDN"]] = record["IP"]
    try:
        if all_ip[fqdn] == ip:
            return f"""The IP for "{fqdn}" is already: {ip}"""
        else:
            record_id = str(to_db("userdb", "records",
                                  {"FQDN": fqdn, "IP": ip,
                                   "date_time": str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))}).inserted_id)
            try:
                update_db("userdb", "users", {"_id": str(current_user.id)}, {"$push": {"records": record_id}})
            except:  # expect that no records exist
                update_db("userdb", "users", {"_id": str(current_user.id)}, {"$set": {"records": [record_id]}})

            #add_dns_record(fqdn, ip)
    except:
        return f"""The FQDN, "{fqdn}", is not registered"""

    # from .restart_dns import restart_dns
    # restart_dns()
    if DnsZone(fqdn, ip)['error']:
        return f"""There has been an error with "{fqdn}",  {ip}"""
    else:
        return f"""The IP for "{fqdn}" previously was: {all_ip[fqdn]}. Now it has is set to: {ip}"""

def api_history():
    from bson.objectid import ObjectId
    record_fqdn = request.args.get('fqdn')
    user_id = request.args.get('id')
    id_tobe_shown = []
    for item in all_from_db("userdb", "records", {"FQDN": record_fqdn}):
        id_tobe_shown.append(ObjectId(item["_id"]))

    existingrecords = ""
    for id in id_tobe_shown:
        record = from_db("userdb", "records", {"_id": ObjectId(id)})
        existingrecords += f""" <tr>
                                    <td style="padding:0 10px">{record["FQDN"]}</td>
                                    <td style="text-align:center; padding:0 10px">{record["IP"]}</td>
                                    <td style="padding:0 10px">{record["date_time"]}</td>
                                </tr>"""
    return f""" <h2>History of "{record_fqdn}". The DNS records</h2><br>
                <table style="border:1px solid black">
                    <tr>
                        <th>FQDN</th>
                        <th>IP</th>
                        <th>Time</th>
                    </tr>
                    {existingrecords}
                </table>
    """