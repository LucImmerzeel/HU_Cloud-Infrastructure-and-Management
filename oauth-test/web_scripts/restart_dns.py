import psutil
import subprocess
from .stop_dns import stop_dns
import os
import time
from .mongodb import from_db, all_from_db

ZONES_PATH = os.environ.get("ZONES_PATH", None)
INTERPRETER = os.environ.get("INTERPRETER", None)
DNSSERVER = os.environ.get("DNSSERVER", None)
DNSSERVER_PATH = os.environ.get("DNSSERVER_PATH", None)
PIDFOLDER = os.environ.get("PIDFOLDER", None)


def restart_dns():
    returnString = stop_dns()

    # Removing all existing
    for filename in os.listdir(ZONES_PATH):
        os.remove(os.path.join(ZONES_PATH, filename))

    make_zones()

    subprocess.Popen([INTERPRETER + " " + DNSSERVER], stdout=subprocess.PIPE, shell=True, cwd=DNSSERVER_PATH)
    #print("cd /home/ec2-user/cim_proj/HU_Cloud-Infrastructure-and-Management/dns-server/; ", INTERPRETER, DNSSERVER)
    time.sleep(0.5)

    with open(PIDFOLDER, "r") as pid_file:
        pid = int(pid_file.read())

    return returnString + "<br>" + """<a>The DNS-server is restarting with de PID of: {}</a>
                                      <br><a class="button" href="/portal">Back</a>""".format(pid)


def make_zones():
    from check_if_ip import is_valid_ipv4_address
    # print(from_db("userdb", "records", {"FQDN": "Test.LucImmerzeel.nl"}))
    # array = list(all_from_db("userdb", "records", {"FQDN": "Test.LucImmerzeel.nl"}))
    # print(array)

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
            for x in range(-3, len(split_zone) * -1 - 1, -1):
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
            for x in range(-3, len(split_zone) * -1 - 1, -1):
                subsubdomains.append(split_zone[x])
                # print(subsubdomains)
            subdomains.append(subsubdomains)
            top_zone.append(subdomains)
            zone_list.append(top_zone)
    print(zone_list)
    print(all_ip)

    for zone in zone_list:
        a_records = ""
        for subdomain in zone[1]:
            try:
                a_records += f""", {{"name": "{subdomain[0] + "." + zone[0]}", "ttl": 400, "value": "{all_ip[subdomain[0] + "." + zone[0]]}" }} """
            except:
                continue
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




        with open(os.path.join(ZONES_PATH, zone[0] + ".zone"), "w") as zone_file:
            zone_file.write(f"""     /{{  "$origin": "{zone[0]}",
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
