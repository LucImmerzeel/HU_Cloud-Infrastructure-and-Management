import socket
from dns_generator import ClientHandler
import os


PIDFOLDER = os.environ.get("PIDFOLDER", "/home/ec2-user/cim_proj/HU_Cloud-Infrastructure-and-Management/dns-server/pid.id")

IP = "0.0.0.0"
PORT = 53


def main():
    print(os.getpid())
    with open(PIDFOLDER, "w") as pid_file:
        pid_file.write(str(os.getpid()))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))
    print("DNS Listening on {0}:{1} ...".format(IP, PORT))
    while True:
        data, address = sock.recvfrom(650)
        client = ClientHandler(address, data, sock)
        client.run()


if __name__ == "__main__":
    main()

