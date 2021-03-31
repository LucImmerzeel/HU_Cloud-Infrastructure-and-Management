import os

ZONES_PATH = os.environ.get("ZONES_PATH", None)


def add_dns_record(fqdn, ip):
    split_fqdn = fqdn.split(".")
    base_fqdn = split_fqdn[-1] + split_fqdn[-2]

    if os.path.exists(os.path.join(ZONES_PATH, base_fqdn + ".zone")):
        os.remove(os.path.join(ZONES_PATH, base_fqdn + ".zone"))

    sparate_records = ""
    for separate in split_fqdn[::-1]:
        if separate == split_fqdn[-1] or separate == split_fqdn[-2]:
            continue
        else:
            f""""a": [{{"name": "{separate}", "ttl": 400, "value": "{ip}" }}]"""
        f""""a": [{{"name": "@", "ttl": 400, "value": "{ip}" }}]"""

    with open(os.path.join(ZONES_PATH, base_fqdn + ".zone"), "w") as zone_file:
        zone_file.write(f""" /{{
                                        "$origin": "{base_fqdn}",
                                        "$ttl": 3600,

                                        "soa": {{
                                            "mname": "ns1.{base_fqdn}",
                                            "rname": "admin.{base_fqdn}",
                                            "serial": "{{time}}",
                                            "refresh": 3600,
                                            "retry": 600,
                                            "expire": 604800,
                                            "minimum": 86400}},

                                        "ns": [
                                            {{"host": "ns1.{base_fqdn}"}},
                                            {{"host": "ns2.{base_fqdn}"}}
                                        ],
                                        {sparate_records}


                                    }}""")


def remove_dns_record():
    return