#!/usr/bin/python3
#   prints vm/container network info
#
import socket

if __name__ == "__main__":

    host_name = socket.gethostname()
    ip = socket.gethostbyname( host_name )

    print( "host_name", host_name, "\nIp Address", ip )

    while True:
        print("Enter a host, leave empty to use current host")
        inhost = input()

        print("Enter a port or for address info, or any char to exit")
        inport = input()

        try:
            inport = int(inport)
        except:
            print("exit")
            exit()

        if not inhost or not inhost.replace(" ", ""):
            inhost = host_name

        # getaddrinfo returns (family, type, proto, canonname, sockaddr)
        info = socket.getaddrinfo(inhost, inport, family=socket.AF_INET )   ## see https://docs.python.org/3/library/socket.html#socket.getaddrinfo
        for i in info:
            print(i)

