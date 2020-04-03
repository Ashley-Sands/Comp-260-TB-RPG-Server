import socket
import time
import threading
import DEBUG

from client import Client
from message import Message
from Game.Main import Main as MainGame
from StaticActions import StaticActions

from constants import *


clients = {}        # ref to all clients within all games :)
client_count = 0
clients_max = 50

accepting_conn_thread = None
accepting_connections = True
thread_lock = threading.Lock()


def accept_clients(socket_):
    global accepting_connections, client_count
    DEBUG.DEBUG.print("starting to accept clients")

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
                # TODO: this should be status protocol, type server, ok ummm no...
                send_client_message("is full, try again later...", client_key )
                time.sleep( 0.05 )  # give it a sec to send the message (TODO: Improve!)
                clients[client_key].close()
                continue

            # request the identity of the client
            identity_msg = Message( client_key, 'i')
            new_message = identity_msg.new_message( SERVER_NAME, "" )
            identity_msg.message = new_message
            identity_msg.to_clients = [ client_key ]

            thread_lock.release()

            send_message( identity_msg )

            # count and release our client into the wild!
            client_count += 1
            DEBUG.DEBUG.print("new client accepted!")
        except Exception as e:
            DEBUG.DEBUG.print("error on socket, ", e)
            break

        time.sleep(0.5)

    thread_lock.acquire()
    accepting_connections = False
    thread_lock.release()

    DEBUG.DEBUG.print("that's enough clients for now")


def get_client_list( except_clients=[], game=None ):
    """Gets a list of all clients, ignoring the except_clients
    if game is passed in then it will only get clients from that game
    :param except_clients:  list of clients to excuse from the list
    :param game:            if supplied the game to get the clients from
    :return:                a list of clients
    """
    client_list = []

    thread_lock.acquire()

    if game is None:
        client_list = [*clients]
    else:
        client_list = [*game.players]

    thread_lock.release()

    for ec in except_clients:
        if ec in client_list:
            client_list.remove(ec)

    return client_list


def get_client(client_key):
    """Get a single client returns none if not found"""
    if client_key in clients:
        return clients[client_key]
    else:
        return None


def get_games(available_only=True):
    """
    :return list of games]
    """

    # TODO: add games...
    if not available_only:
        return game

    avail_games = []

    for g in game:
        if g.can_join():
            avail_games.append( g )

    return avail_games


def send_message(message_obj):

    DEBUG.DEBUG.print( "Sending to", message_obj.to_clients, "type:", message_obj.identity )
    for c in message_obj.to_clients:
        DEBUG.DEBUG.print("Sending to", c, "type:", message_obj.identity)
        clients[c].que_message(message_obj)


def send_client_message( message, client_key ):

    new_client_message = Message( client_key, 'm' )
    new_message = new_client_message.new_message( SERVER_NAME, message )
    new_client_message.message = new_message
    new_client_message.to_clients = [ client_key ]

    send_message( new_client_message )

if __name__ == "__main__":

    DEBUG.DEBUG.init()
    game = [MainGame( "MG-0", send_message )] # , MainGame( "MG-1", send_message ), MainGame( "MG-2", send_message )]

    # Spin up the socket
    socket_inst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_inst.bind(("0.0.0.0", 8222))
    socket_inst.listen(clients_max)

    # initialize the game and singletons actions
    Message.initialize_actions(None, send_message, get_client_list, get_client, get_games)

    # start a thread to receive connections
    accepting_conn_thread = threading.Thread(target=accept_clients, args=(socket_inst,))
    accepting_conn_thread.start()

    DEBUG.DEBUG.print ("waiting for connections...")

    # process all the data :)
    while True:
        for k in [*clients]:
            # clean up any lost clients
            if not clients[k].is_valid():
                # Clean up the client and make sure that all the threads have stopped
                clients[k].close()
                # notify the others that the client is dead to us
                StaticActions.send_client_status(False, "Client has disconnected", k, clients[k].name,
                                                 get_client_list, send_message)
                # kill the zombie before it eats all out brains
                if clients[k].get_active_game() is not None:
                    # remove all ref from the game.
                    # TODO: put in close function in player
                    cliGame = clients[k].get_active_game()

                    if clients[k].game_player_id in cliGame.game.playerId:
                        del cliGame.game.playerId[ clients[k].game_player_id ]

                    if k in cliGame.game.ready:
                        del cliGame.game.ready[ k ]

                    del cliGame.players[ k ]
                del clients[ k ]

                DEBUG.DEBUG.print("Lost client", k)
                continue

            for i, g in enumerate(game):
                if not g.is_valid():
                    DEBUG.DEBUG.print("Game ["+str(i)+"] invalid, starting new")
                    game[i] = MainGame( "MG-"+str(i), send_message )

            try:
                while not clients[k].received_queue.empty():
                    recv_msg = clients[k].received_queue.get(block=True, timeout=None)
                    recv_msg.run_action()
            except Exception as e:
                DEBUG.DEBUG.print(e, "\nMain Line ~183", message_type=DEBUG.DEBUG.MESSAGE_TYPE_ERROR)

        # time.sleep(0.5)
