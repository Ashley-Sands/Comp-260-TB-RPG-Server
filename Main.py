import socket
import time
import threading

from client import Client
from message import Message
from Game.Main import Main as MainGame

SERVER_NAME = "SERVER"

game = MainGame()

clients = {}        # ref to all clients within all games :)
client_count = 0
clients_max = 4

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

            client_key = "client-" + str(client_count)
            client_name = client_key

            clients[client_key] = Client(client_name, client, client_key)
            clients[client_key].start()

            # for some reason the connections get queued up if they are not excepted
            # even if they disconnect.
            # so accept them tell um we're full and slam the door in there face
            if len(clients) > clients_max:
                send_client_message("is full, try again later...", client_key )
                time.sleep( 0.05 )  # give it a sec to send the message (TODO: Improve!)
                clients[client_key].close()
                continue

            thread_lock.release()

            # notify other users that someone has connected :)
            send_client_status(True, client_key, client_name)

            # count and release our client into the wild!
            client_count += 1
            print("new client accepted!")
        except Exception as e:
            print("error on socket, ", e)
            break

        time.sleep(0.5)

    thread_lock.acquire()
    accepting_connections = False
    thread_lock.release()

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
        clients[c].que_message(message_obj)

def send_client_status( status, client_key, client_name ):

    new_client_message = Message( client_key, 's' )
    new_message = new_client_message.new_message( client_name, status )
    new_client_message.message = new_message
    new_client_message.to_clients = get_client_list( [ client_key ] )

    send_message( new_client_message )

def send_client_message( message, client_key ):

    new_client_message = Message( client_key, 'm' )
    new_message = new_client_message.new_message( SERVER_NAME, message )
    new_client_message.message = new_message
    new_client_message.to_clients = [ client_key ]

    send_message( new_client_message )

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
                # notify the others that the client is dead to us
                send_client_status(False, k, clients[k].name)
                # kill the zombie before it eats all out brains
                del clients[k]
                print("Lost client", k)
                continue

            try:
                while not clients[k].received_queue.empty():
                    recv_msg = clients[k].received_queue.get(block=True, timeout=None)
                    recv_msg.run_action()
            except Exception as e:
                print(e)

        time.sleep(0.5)
