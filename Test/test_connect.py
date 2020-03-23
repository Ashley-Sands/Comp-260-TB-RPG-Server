# Fake Client...
import socket
import time
import json

host = "DESKTOP-S8CVUEK" # "159.65.80.187" # localhost_0"
port = 8223 # 8222

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
    print("waiting for 1 sec")
    time.sleep(1)
    print("pre send")
    try:
        #send_time = time.time()
        #sock.send(b'ping')
        data = sock.recv(512)[3:].decode("utf-8")

        print("data", data)

        msg = json.loads( data )
        msg["nickname"] = "Helloo World!"
        msg = json.dumps(msg)

        msg_len = len( msg ).to_bytes( 2, "big" )
        msg_type = ord( 'i' ).to_bytes( 1, "big" )

        sock.send(msg_len + msg_type + msg.encode())
        print("sent", msg_len + msg_type + msg.encode())

        #receive_time = time.time()
    except Exception as e:
        print("failed", e)
        pass
