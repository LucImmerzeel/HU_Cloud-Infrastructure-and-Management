import psutil
import subprocess
from .stop_dns import stop_dns
import os
import time


INTERPRETER = os.environ.get("INTERPRETER", None)
DNSSERVER = os.environ.get("DNSSERVER", None)
PIDFOLDER = os.environ.get("PIDFOLDER", None)


def restart_dns():
    returnString = stop_dns()

    subprocess.Popen([INTERPRETER, DNSSERVER], stdout=subprocess.PIPE, shell=True)
    time.sleep(0.5)

    with open(PIDFOLDER, "r") as pid_file:
        pid = int(pid_file.read())

    return returnString + "<br>" + """<a>The DNS-server is restarting with de PID of: {}</a>
                                      <br><a class="button" href="/portal">Back</a>""".format(pid)
