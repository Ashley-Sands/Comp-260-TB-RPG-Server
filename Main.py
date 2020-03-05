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

            client_name = "client" + str(client_count)
            clients[client_name] = Client(client_name, client, client_name)
            clients[client_name].start()

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


def get_client_list( except_clients=[] ):

    thread_lock.acquire()

    client_list = [*clients]

    thread_lock.release()

    for ec in except_clients:
        if ec in clients:
            client_list.remove(ec)

    return client_list


def get_client(client_key):
    """Get a single client returns none if not found"""
    if client_key in clients:
        return clients[client_key]
    else:
        return None


def send_message(message_obj):

    for c in message_obj.to_clients:
        print("Sending to", c)
        clients[k].que_message(message_obj)


if __name__ == "__main__":

    # Spin up the socket
    socket_inst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_inst.bind(("127.0.0.1", 8222))
    socket_inst.listen(5)                   # Allow up to 5 connection. TODO: make not magic!

    # initialize the game and singletons actions
    # TODO: Add Game Instance
    Message.initialize_actions(None, send_message, get_client_list, get_client)

    # start a thread to receive connections
    accepting_conn_thread = threading.Thread(target=accept_clients, args=(socket_inst,))
    accepting_conn_thread.start()

    print ("\nwaiting for connections...")

    # process all the data :)
    while True:
        for k in [*clients]:
            # clean up any lost clients
            if not clients[k].is_valid():
                # Clean up the client and make sure that all the threads have stopped
                clients[k].close()
                del clients[k]  # kill the zombie before it eats all out brains
                print("Lost client", k)
                continue

            try:
                while not clients[k].received_queue.empty():
                    recv_msg = clients[k].received_queue.get(block=True, timeout=None)
                    recv_msg.run_action()
            except Exception as e:
                print(e)

        time.sleep(0.5)
