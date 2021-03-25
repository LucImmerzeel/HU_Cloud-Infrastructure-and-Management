#!/usr/bin/env python3
import socket, os

from dns_generator import ClientHandler

# From: https://github.com/akapila011/DNS-Server

# Global variables
IP = "0.0.0.0"
PORT = 53


def main():
    print(os.getpid())
    with open("C:/Users/StudyUser/PycharmProjects/HU_Cloud-Infrastructure-and-Management/dns-server/pid.id", "w") as pid_file:
        pid_file.write(str(os.getpid()))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))
    print("DNS Listening on {0}:{1} ...".format(IP, PORT))
    while True:
        data, address = sock.recvfrom(650)
        client = ClientHandler(address, data, sock)
        client.run()


if __name__ == "__main__":
    import pymongo
    import sys, os

    sys.path.append(os.path.realpath('..'))
    main()
    #mongoclient = pymongo.MongoClient("mongodb://dbUser:vI0PhpVCvNcOMVQg@103.86.96.100/UserDB?retryWrites=true&w=majority")
    mongoclient = pymongo.MongoClient("mongodb://dbUser:vI0PhpVCvNcOMVQg@103.86.96.100:27017/")
    # mongodb = mongoclient["UserDB"]
    print(mongoclient.list_database_names())
    print("Test")
    mongodb = mongoclient.test

