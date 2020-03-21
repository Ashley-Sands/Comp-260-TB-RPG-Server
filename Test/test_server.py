# test server (to test passthroug connection)

import socket
import Common.database as database

host = "DESKTOP-S8CVUEK"
port = 8223

connected = False

db = database.Database()

active_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
active_socket.bind( (host, port) )
active_socket.listen( 99 )

while not connected:
    print("waiting for connections @ ", (host, port))
    client_sock, addr = active_socket.accept()
    print( "client accepted @ ", addr )
    connected = True

while True:
    print("waiting to recive")
    try:
        data = client_sock.recv(100)
        print (data)
    except Exception as e:
        print ("failed", e)
