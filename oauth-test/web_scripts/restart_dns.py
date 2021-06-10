#!/usr/bin/python3
import paramiko
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
CERTFILE = os.environ.get("CERTFILE", None)
CERTBASE = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAn0shr3TklDyNG6AYtHb68KqbrKQQBZLXDRxmEnFi3ZLod4Qk
Dyu4hLuMnrVJ1H8vfUegissyLTLEmnCPXHPJgL9fA4P4PVBRLphGVSw0EsVBxiHf
Z3Zj+DBs2JZfVWle10G1CsSLdV4FZ7AtrejKsGUGu0xL8pXSJokiW3eeEUakQetf
6JlqFMqR3i2Tyn/9tWClsMfiEpYeJblR8lR2KtJ53CHSUeCJkEKA4yqTyMPlXDUK
j5huSpOoQDkoc8JmhRAEIk2MoXYSoEXs2bBL1I1tnAF7XREhaOvACXT/uCWC5LW5
YUCe808jB/PFweIkFo9WRi1o4AVIwufwxg9kdwIDAQABAoIBADu78OXa79ym2EOD
xb/m3jNhxv72hwuQBRTlkWFZI7nzXTl0VBFcU9Vyf0kEsqr9BtH0CkAB8s8AOrmv
fBMvWGDvYrHuyygy9j6C290UtnJThlbGXQBvZQ2tGyQdP6LH4MjX2wwuqB1bJKu9
ZWPR6DA9skiKU/CkPio1Qq0KLjxLqPW/NGRHa2ZXWPpZN7+eea0TTXiwTpcVFSfe
fouvwVwWY2wzQjvfr+PT7uU3x4j3YcCuzfGNZbI+cQvgrlh36kt7gOEey+8yIc/N
QJ+COK5XKOfTiwyovkKx5oFy9Z4E0C3kIE9YP1YyRLynylp+ii9MQdrdgUrHRVhz
Ig0OAAECgYEA4QL4qIla4Kav5ljbbJPn6Wfr1iJSuUNVibxtDyF8817PIaZsCLIK
/Erfg6BeMsWcf4M3Z3awcD0NjhzV6W62/RqJ21rKdlDwns3UA5QgJZBtjkLsn+2y
VdU8/zE1rLFkO8G9XVJI+AqoPV2KreH3C6SgW/F6fSE78dww2MV0hcsCgYEAtTsy
RwCfCklorVYhoZ8He4P83hklwBDhc8bChwsGtVcZWYQj+Hd7GJFYy1UP6avU8+4m
0W1JwA57EV0z+RdQDLbMB9CD84CKm81JvXjd5cKgTAZzqRl/WR/Y/aSmFYQldpvC
NjBg1Rd38y1Hr9nTYU0Id0G0oKiygTzLJqrFZoUCgYEAzLeRWHUvc3j0TJTHfi/L
LbZZAUfVD61NY7VFXCDRt/KobSsm23pxOD0+wljjmznjOrg9biq0OEmzzXo6vNj4
L6s3hZVC4wadBT6rCF56KPMQWgBVnOP7/s+1YVB6TxZN5XhNO1yj+thnXP2AMNeH
ltY+96fqE3JrQY9d+bscWqUCgYBn6xCyS/XmBR/jvK6+KR02QwGdLNhLoKJWK9Nh
cf4fv1jGzpF9qK1J8hXzScw9Fg2e7aEOl1chrGv/Ee16WFbLY4nstTDkUIGqQvWU
kpjSZV5bGZv6i6dNKIjZMC8XyVVeBIRBZE4yAioCo6UmfYXKlkxTbbawJOtuVbi7
bFKSrQKBgCCI2nDClAKMThkrBmryx5Vm0ForVtIzBUufRFbFVAJcIq4i4/rVWC60
eOhSyf/49RAYJoJ/pIIMXwgvfIXoR7ogb3TcAh4OcnEjkqE8IhG7ksWUkyszP9rk
OW6qtBnz6K0msLg9Bjq0wMJSjsAJTJyRIKeIu9SIqdvXdNCjTRZL
-----END RSA PRIVATE KEY-----"""#os.environ.get("CERTBASE", None)


def restart_dns():
    returnString = "" #"stop_dns()"

    # Removing all existing
    #for filename in os.listdir(ZONES_PATH):
    #    os.remove(os.path.join(ZONES_PATH, filename))

    make_zones()

    #subprocess.Popen([INTERPRETER + " " + DNSSERVER], stdout=subprocess.PIPE, shell=True, cwd=DNSSERVER_PATH)
    #print("cd /home/ec2-user/cim_proj/HU_Cloud-Infrastructure-and-Management/dns-server/; ", INTERPRETER, DNSSERVER)
    #time.sleep(0.5)

    #with open(PIDFOLDER, "r") as pid_file:
    #    pid = int(pid_file.read())

    return returnString + "<br>" + """<a>The DNS-server is restarting with de PID of: {}</a>
                                      <br><a class="button" href="/portal">Back</a>"""#.format(pid)




def make_zones():
    from .check_if_ip import is_valid_ipv4_address
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


    command = f"""
sudo tee {DNSSERVER_PATH} <<EOF
options {{  listen-on port 53 {{ 127.0.0.1; 0.0.0.0/0; }};
            directory       "/var/named";
            dump-file       "/var/named/data/cache_dump.db";
            statistics-file "/var/named/data/named_stats.txt";
            memstatistics-file "/var/named/data/named_mem_stats.txt";
            recursing-file  "/var/named/data/named.recursing";
            secroots-file   "/var/named/data/named.secroots";
            allow-query     {{ any; }};
            recursion no;
    
            dnssec-enable yes; dnssec-validation yes;
    
            /* Path to ISC DLV key */
            bindkeys-file "/etc/named.root.key";
    
            managed-keys-directory "/var/named/dynamic";
    
            pid-file "/run/named/named.pid";
            session-keyfile "/run/named/session.key";   }};

logging {{channel default_debug {{file "data/named.run"; severity dynamic;}};}};
zone "." IN {{ type hint; file "named.ca"; }};
include "/etc/named.rfc1912.zones";
include "/etc/named.root.key";
EOF
"""
    print(command)
    to_ssh(command)

    command = f"sudo rm -r {ZONES_PATH}/*"
    print(command)
    to_ssh(command)

    for zone in zone_list:
        command = f"""
sudo tee -a {DNSSERVER_PATH} <<EOF
zone "{zone[0]}" {{
    type master;
    file "{ZONES_PATH}{zone[0]}.zone";
}};
EOF
"""
        print(command)
        to_ssh(command)


        b_records
        a_records = f"""
\$TTL    3h
@       IN      SOA     ns1.{zone[0]}. admin.{zone[0]}. (
                  1        ; Serial
                  3h       ; Refresh after 3 hours
                  1h       ; Retry after 1 hour
                  1w       ; Expire after 1 week
                  1h )     ; Negative caching TTL of 1 day
@       IN      NS      ns1.{zone[0]}."""

        for subdomain in zone[1]:
            try:
                b_records += f"""
{subdomain[0]}  IN      A       {all_ip[subdomain[0] + "." + zone[0]]}"""
            except:
                continue
        if b_records == "":
            b_records = f"""
@       IN      A       {all_ip[subdomain[0] + "." + zone[0]]}"""

        a_records += b_records + """
ns1     IN      A       127.0.0.1"""

        """
        ns1                     IN      A       192.168.0.10
        ns2                     IN      A       192.168.0.11
        www                     IN      CNAME   linuxconfig.org.
        mail                    IN      A       192.168.0.10
        ftp                     IN      CNAME   linuxconfig.org.
        """

        # print(os.path.join(ZONES_PATH, zone[0] + ".zone"))
        # print(f""" {{  "$origin": "{zone[0]}",
        #                     "$ttl": 3600,
        #
        #                     "soa": {{
        #                         "mname": "ns1.{zone[0]}",
        #                         "rname": "admin.{zone[0]}",
        #                         "serial": "{{time}}",
        #                         "refresh": 3600,
        #                         "retry": 600,
        #                         "expire": 604800,
        #                         "minimum": 86400}},
        #
        #                     "ns": [{{"host": "ns1.{zone[0]}"}}, {{"host": "ns2.{zone[0]}"}}],
        #                     "a": [{a_records[1:]}]}}""")


        print(a_records)

        # with open(os.path.join(ZONES_PATH, zone[0] + ".zone"), "w") as zone_file:
        #     zone_file.write(f"""     {{  "$origin": "{zone[0]}",
        #                                 "$ttl": 3600,
        #
        #                                 "soa": {{
        #                                     "mname": "ns1.{zone[0]}",
        #                                     "rname": "admin.{zone[0]}",
        #                                     "serial": "{{time}}",
        #                                     "refresh": 3600,
        #                                     "retry": 600,
        #                                     "expire": 604800,
        #                                     "minimum": 86400}},
        #
        #                                 "ns": [{{"host": "ns1.{zone[0]}"}}, {{"host": "ns2.{zone[0]}"}}],
        #                                 "a": [{a_records[1:]}]}}""")

        command = f"""  
sudo tee {ZONES_PATH}{zone[0]}.zone <<EOF
{a_records}
EOF
"""
        print(command)
        to_ssh(command)
        command = f"""sudo systemctl restart named"""
        print(command)
        to_ssh(command)


def to_ssh(command):
    import base64
    import paramiko
    from io import StringIO

    privkey = paramiko.RSAKey.from_private_key(StringIO(CERTBASE))
    #privkey = paramiko.RSAKey.from_private_key_file(CERTFILE)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #client.get_host_keys().add('127.0.0.1')
    client.connect(DNSSERVER, username='ec2-user', pkey=privkey)
    stdin, stdout, stderr = client.exec_command(command)

    print("Output: " + stdout.read().decode('utf-8'))
    print("Error: " + stderr.read().decode('utf-8'))
    client.close()
    return stdin, stdout, stderr
