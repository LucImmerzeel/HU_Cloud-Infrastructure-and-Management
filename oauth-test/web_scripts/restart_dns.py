import psutil
import subprocess


def restart_dns():
    returnString = ""

    with open("C:/Users/StudyUser/PycharmProjects/HU_Cloud-Infrastructure-and-Management/dns-server/pid.id", "r") as pid_file:
        pid = int(pid_file.read())

    try:
        p = psutil.Process(pid)
        p.terminate()
    except psutil.NoSuchProcess:
        returnString += """ <a>No process found with pid: {}</a><br>""".format(pid)

    subprocess.Popen(["powershell",
                      "C:/Users/StudyUser/PycharmProjects/HU_Cloud-Infrastructure-and-Management/venv/Scripts/python.exe",
                      "C:/Users/StudyUser/PycharmProjects/HU_Cloud-Infrastructure-and-Management/dns-server/dns-server.py"],
                     stdout=subprocess.PIPE, shell=True)

    return returnString + """ <a>The DNS-server is restarting with de PID of: {}</a>""".format(pid)
