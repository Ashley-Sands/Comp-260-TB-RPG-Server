# Fake Client...
import socket
import time
host = "159.65.80.187" # localhost_0"  # "DESKTOP-S8CVUEK"
port = 8222

connected = False
sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
print(time.time())
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
        send_time = time.time()
        sock.send(b'ping')
        data = sock.recv(100)
        receive_time = time.time()
        print("Ping:", (receive_time-send_time)*1000.0, "ms")
    except:
        print("failed")
        pass
