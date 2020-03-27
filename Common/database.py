import Common.sql_query as sql
import hashlib
import time
import Common.DEBUG as DEBUG
import random

class Database:

    def __init__( self ):

        # make sure that the database has been set up
        self.database = sql.sql_query("tb_rpg", True)

        DEBUG.LOGS.print( "Database Inited Successfully!" )

    def valid_user_response( self, user_data, reg_key ):
        """Makes sure there was only 1 responce, removes dups (both copys)"""
        # if theres more than one result somethings gone wrong
        # remove both from the active users list
        if len(user_data) > 1:
            self.database.remove_row("active_users", ["reg_key"], [reg_key])
            DEBUG.LOGS.print("Multiple reg keys found", user_data, message_type=DEBUG.LOGS.MSG_TYPE_FATAL)
            return False
        elif len(user_data) == 0:
            return False

        return True

    def add_new_client( self, nickname ):
        """
            Adds a new client
        :return:    tuple of the client id and reg_id tuple(cid, rid)
        """

        reg_key = hashlib.sha224("{0}{1}".format( nickname, time.time() ).encode() ).hexdigest()

        self.database.insert_row("active_users", ["nickname", "reg_key"], [nickname, reg_key])
        uid = self.database.select_from_table( "active_users", ["uid, reg_key"], ["reg_key"], [reg_key] )[0][0]

        client_id = uid

        return client_id, reg_key

    def get_random_name( self ):

        rand = random.random()
        query = "SELECT word FROM {0} WHERE id >= {1} * (SELECT MAX(id) FROM {0})"
        adj = self.database.execute( query.format( "names_list_adjective", rand ), [] )[0][0]

        rand = random.random()
        noun = self.database.execute( query.format( "names_list_nouns", rand ), [] )[0][0]

        return adj[0:1].upper() + adj[1:].lower() + " " + noun[0:1].upper() + noun[1:]

    def select_client( self, reg_key ):
        """
            Selects users by there reg key
        :param reg_key: the users reg key
        :return:        if found the clients id nickname otherwise None
        """

        user_data = self.database.select_from_table("active_users", ["uid", "nickname", "lobby_id"], ["reg_key"], [reg_key])

        if not self.valid_user_response( user_data, reg_key ):
            return None

        return user_data[0]

    def get_client_lobby( self, reg_key ):

        user_data = self.database.select_from_table("active_users", ["lobby_id"], ["reg_key"], [reg_key])

        if not self.valid_user_response( user_data, reg_key ):
            return None
        print(user_data)
        return user_data[0][0]

    def get_lobby_host( self, lobby_id ):

        query = "SELECT lobby_host.host " \
                "FROM lobbies " \
                "JOIN lobby_host " \
                "ON lobbies.lobby_host_id=lobby_host.uid " \
                "WHERE lobbies.uid=%s"

        host = self.database.execute(query, [lobby_id]) # self.database.select_from_table("lobby_host", ["host"], ["uid"], [lobby_host_id])
        print(host)
        if len(host) != 1:
            host = None
        else:
            host = host[0][0]

        return host

    def update_client_nickname( self, reg_key, nickname ):

        self.database.update_row("active_users",
                                 ["nickname"], [nickname],
                                 ["reg_key"],  [reg_key] )

    def add_new_lobby( self ):

        # find the lobby host with the least active lobbies
        used_host = "SELECT lobby_host.uid, COUNT(lobby_host.uid) " \
                "FROM lobbies " \
                "JOIN lobby_host ON lobbies.lobby_host_id=lobby_host.uid " \
                "GROUP BY lobby_host.uid " \
                "WHERE lobbies.game_id < 0 "

        all_lobby_host = "SELECT * FROM lobby_host"

        # return (host id, lobby count)
        # if theres more ahost than uhost then theres host without lobbies
        # uhost_rows = self.database.execute(used_host, []) # TODO: make dynamic
        ahost_rows = self.database.execute(all_lobby_host, [])

        min_host = ahost_rows[0] # (-1, 9999)
        DEBUG.LOGS.print( "--------------->>>", ahost_rows )

        # find the host with the list lobbies
        # for uh in uhost_rows :
        #    if r[1] < min_host[1]:
        #        min_host = r

        self.database.insert_row("lobbies", ["level_id", "lobby_host_id"], ["1", min_host[0]])    # TODO: this should just select a level at random.
        DEBUG.LOGS.print( "---------------<<<", self.database.select_from_table("lobbies", ["*"]) )
        DEBUG.LOGS.print( "---------------<<<", self.database.select_from_table("lobby_host", ["*"]) )

    def available_lobby_count( self ):

        return self.database.select_from_table("lobbies", ["COUNT(game_id)"], ["game_id<"], ["0"], override_where_cols=True)[0][0]

    def select_all_available_lobbies( self ):
        """

        :return: (tuple) (list (a row) of tuples (the columns), list of current players)
                        [(lobby id, level id, level name, min players, max players), ...],
                        [current_players]...
        """
        query = "SELECT lobbies.uid, levels.uid, levels.name, levels.min_players, levels.max_players" \
                " FROM lobbies JOIN levels ON lobbies.level_id=levels.uid WHERE lobbies.game_id < 0"

        # stitch the current_players count
        lobbies = self.database.execute(query, [])
        current_players = []

        for l in lobbies:
            current_players.append( self.get_lobby_player_count( l[0] ) )

        return lobbies, current_players

    def get_lobby_player_count( self, lobby_id ):

        return self.database.select_from_table("active_users", ["COUNT(lobby_id)"], ["lobby_id"], [lobby_id])[0][0]

    def get_lobby_player_list( self, lobby_id ):
        """
            get a list of players in lobby id
        :param lobby_id:
        :return: tuple of list ( [uid], [nicknames] )
        """
        row = self.database.select_from_table("active_users", ["uid", "nickname"], ["lobby_id"], [lobby_id])
        uid = []
        nicknames = []

        for r in row:
            uid.append(r[0])
            nicknames.append(r[1])

        return uid, nicknames


    def join_lobby( self, client_id, lobby_id ):
        """ Joins game lobby

        :return: True if successful otherwise False
        """

        # check that the user can join the lobby
        query = "SELECT levels.max_players " \
                "FROM lobbies JOIN levels ON lobbies.level_id = levels.uid " \
                "WHERE lobbies.game_id < 0 AND lobbies.uid = %s"

        lobby = self.database.execute( query, [lobby_id] )
        current_players = self.get_lobby_player_count( lobby_id )

        if len(lobby) != 1:  # error not found
            return False, "Lobby Not Found"

        if current_players < lobby[0][0]:
            self.database.update_row( "active_users", ["lobby_id"], [lobby_id], ["uid"], [client_id] )
            return True, ""

        return False, "Server is full"

    def add_lobby_host( self, host ):

        self.database.insert_row( "lobby_host", ["host"], [host] )

        return self.database.select_from_table( "lobby_host", ["uid"], ["host"], [host] )[0][0]

    def remove_lobby_host( self, host ):
        """Add a new lobby host to the current list of lobbies and returns the new id"""

        self.database.remove_row( "lobby_host", ["host"], [host])
