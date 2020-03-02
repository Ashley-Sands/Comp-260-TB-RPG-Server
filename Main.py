import socket
import time
import threading

from client import Client
from message import Message

clients = {}
client_count = 0

accepting_conn_thread = None
accepting_connections = True
thread_lock = threading.Lock()


def accept_clients(socket_):
    global accepting_connections, client_count
    print("starting to accept clients")

    while True:

        try:
            client = socket_.accept()[0]

            thread_lock.acquire()

            if not accepting_connections:
                break

            clients["client" + str(client_count)] = Client(client)
            clients["client" + str(client_count)].start()
            client_count += 1
            print("new client accepted!")
            thread_lock.release()
        except Exception as e:
            print("error on socket, ", e)

            thread_lock.acquire()
            accepting_connections = False
            thread_lock.release()
            break

        time.sleep(0.5)

    print("that's enough clients for now")


def send_message(msg):

    for k in [*clients]:
        if k != msg.fromClientId:
            clients[k].send_queue.put(msg.message)


if __name__ == "__main__":

    socket_inst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #socket_inst.settimeout(0.0) # prevent the recv function from blocking

    socket_inst.bind(("127.0.0.1", 8222))
    socket_inst.listen(5)

    # start a thread to receive connections
    accepting_conn_thread = threading.Thread(target=accept_clients, args=(socket_inst,))
    accepting_conn_thread.start()

    print ("\nwaiting for connections...")

    #socket_inst.close()

    # process all the data :)
    while True:
        for k in [*clients]:
            # clean up any lost clients
            if not clients[k].is_valid():
                del[clients[k]]
                continue

            try:
                while not clients[k].received_queue.empty():
                    send_message(Message(k, clients[k].received_queue.get(block=True, timeout=None)))
            except:
                pass
        time.sleep(0.5)