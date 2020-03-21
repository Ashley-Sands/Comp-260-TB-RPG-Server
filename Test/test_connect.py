# Fake Client...
import socket
import time
host = "localhost_0"  # "DESKTOP-S8CVUEK"
port = 8222

connected = False
sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

while not connected:
    try:
        sock.connect( (host, port) )
        connected = True
        print("print connection made", sock) # , addr)
    except Exception as e:
        print(e)

while True:
    print("waiting for 3 sec")
    time.sleep(3)
    print("pre send")
    try:
        sock.send(b'helloo Wolrd')
        print("message sent...")
    except:
        print("failed")
        pass
