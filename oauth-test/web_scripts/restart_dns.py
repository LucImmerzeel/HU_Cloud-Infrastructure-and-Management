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

    #all_from_db()


    subprocess.Popen([INTERPRETER + " " + DNSSERVER], stdout=subprocess.PIPE, shell=True, cwd=DNSSERVER_PATH)
    #print("cd /home/ec2-user/cim_proj/HU_Cloud-Infrastructure-and-Management/dns-server/; ", INTERPRETER, DNSSERVER)
    time.sleep(0.5)

    with open(PIDFOLDER, "r") as pid_file:
        pid = int(pid_file.read())

    return returnString + "<br>" + """<a>The DNS-server is restarting with de PID of: {}</a>
                                      <br><a class="button" href="/portal">Back</a>""".format(pid)
