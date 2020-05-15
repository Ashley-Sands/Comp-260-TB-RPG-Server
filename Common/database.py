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

    def remove_client( self, reg_key ):
        """removes a client from the database"""

        self.database.remove_row("active_users", ["reg_key"], [reg_key])

    def get_random_name( self ):

        rand = random.random()
        query = "SELECT word FROM {0} WHERE id >= {1} * (SELECT MAX(id) FROM {0})"
        adj = self.database.execute( query.format( "names_list_adjective", rand ), [], fetch=True )[0][0]

        rand = random.random()
        noun = self.database.execute( query.format( "names_list_nouns", rand ), [], fetch=True )[0][0]

        return adj[0:1].upper() + adj[1:].lower() + " " + noun[0:1].upper() + noun[1:]

    def select_client( self, reg_key ):
        """
            Selects users by there reg key
        :param reg_key: the users reg key
        :return:        if found the clients id nickname and lobby id otherwise None
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

    def clear_client_lobby( self, reg_key ):

        self.database.update_row( "active_users", ["lobby_id"], [-1], ["reg_key"], [reg_key] )

    def get_lobby_host_ids( self, lobby_id ):
        """ gets the lobby host id and game host id (tuple)"""

        query = "SELECT lobby_host_id, game_id " \
                "FROM lobbies " \
                "WHERE uid = %s"

        results = self.database.execute( query, [lobby_id], fetch=True )

        if len( results ) != 1:
            return -1, -1

        return results[0]

    def get_lobby_host_from_lobby_id( self, lobby_id ):

        query = "SELECT lobby_host.host " \
                "FROM lobbies " \
                "JOIN lobby_host ON lobbies.lobby_host_id = lobby_host.uid " \
                "WHERE lobbies.uid = %s"

        results = self.database.execute( query, [lobby_id], fetch=True )

        if len( results ) != 1:
            return None

        return results[0][0]

    def get_lobby_host( self, host_id ):

        query = "SELECT host " \
                "FROM lobby_host " \
                "WHERE uid=%s"

        host = self.database.execute(query, [host_id], fetch=True)
        print(host, query, host_id)
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
        """ Add a new lobby

        :return: true if successful
        """
        # find the lobby host with the least active lobbies
        used_host = "SELECT lobby_host.uid, COUNT(lobby_host.uid) " \
                "FROM lobbies " \
                "JOIN lobby_host ON lobbies.lobby_host_id=lobby_host.uid " \
                "GROUP BY lobby_host.uid " \
                "WHERE lobbies.game_id < 0 "

        min_host = self.get_min_lobby_host()

        if min_host[0] == -1:
            DEBUG.LOGS.print("Unable to add new lobby, no host available.")
            return False

        self.database.insert_row("lobbies", ["level_id", "lobby_host_id"], ["1", min_host])    # TODO: this should just select a level at random.

        return True

    def update_lobby_host( self, lobby_id ):
        """ updates a new lobby

            :return: true if successful
        """
        min_host = self.get_min_lobby_host()

        if min_host[0] == -1:
            DEBUG.LOGS.print("Unable to update lobby id, no host available.")
            return False

        self.database.update_row("lobbies", ["lobby_host_id"], [min_host], ["uid"], [lobby_id])

        return True

    def get_min_lobby_host( self ):
        """Get the lobby host with the least amount of lobbies assigned to it.
           returns: tuple ( lobby_host.uid, lobby_host.host )
        """

        all_lobby_host = "SELECT * FROM lobby_host "

        # find this host with the minimal amout of assigned lobbies.
        lobby_host_assigned_counts_query = "SELECT lobby_host.uid, COUNT( lobbies.lobby_host_id ), lobby_host.host " \
                                           "FROM lobbies " \
                                           "JOIN lobbby_host ON lobby_host.uid = lobbies.lobby_host_id " \
                                           "GROUP by lobby_host.uid"

        lobby_host_assigned_counts = self.database.execute( lobby_host_assigned_counts_query, [], fetch=True )

        min_lobby_count = 9999
        min_lobby = (-1, None)

        for l in lobby_host_assigned_counts:
            if l[1] < min_lobby_count:
                min_lobby = l[0], l[2]
                min_lobby_count = l[1]

        return min_lobby

    def update_lobby_game_host ( self, lobby_id, game_host_id ):
        """ updates the lobbies game host removeing it from the game que"""

        self.database.update_row( "lobbies", ["game_id"], [game_host_id], ["uid"], [lobby_id])

    def get_lobby_row( self, lobby_id ):

        query = "SELECT lobby_host_id, game_id, level_id, game_count " \
                "FROM lobbies " \
                "WHERE uid = %s"
        info = self.database.execute( query, [lobby_id], fetch=True )
        DEBUG.LOGS.print("LOBBY_INFO", info, lobby_id)
        return info[0]

    def clear_lobby_host( self, lobby_id ):

        self.database.update_row( "lobbies", ["lobby_host_id"], [-1], ["uid"], [lobby_id])

    def clear_lobby_host_from_all_lobbies( self, lobby_host_id ):

        self.database.update_row( "lobbies", ["lobby_host_id"], [-1], ["lobby_host_id"], [lobby_host_id])

    def clear_lobby_from_all_users( self, lobby_id ):

        self.database.update_row( "active_users", ["lobby_id"], [-1], ["lobby_id"], [lobby_id])

    def available_lobby_count( self ):

        return self.database.select_from_table("lobbies", ["COUNT(game_id)"], ["game_id<"], ["0"], override_where_cols=True)[0][0]

    def select_all_available_lobbies( self ):
        """

        :return: (tuple) (list (a row) of tuples (the columns), list of current players)
                        [(lobby id, level id, level name, min players, max players), ...],
                        [current_players]...
        """
        query = "SELECT lobbies.uid, levels.uid, levels.name, levels.min_players, levels.max_players " \
                "FROM lobbies JOIN levels ON lobbies.level_id=levels.uid " \
                "WHERE lobbies.lobby_host_id >= 0 OR (lobbies.lobby_host_id < 0 AND lobbies.game_id < 0)"

        # stitch the current_players count
        lobbies = self.database.execute(query, [], fetch=True)
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

    def get_lobby_info( self, lobby_id ):
        """Gets list [Level name, min players and max players]"""

        query = "SELECT levels.name, levels.min_players, levels.max_players " \
                "FROM levels " \
                "JOIN lobbies ON lobbies.level_id = levels.uid " \
                "WHERE lobbies.uid = %s"

        rows = self.database.execute( query, [lobby_id], fetch=True )

        if len(rows) != 1:
            DEBUG.LOGS.print("Did not receive exactly one result (count: ", len(rows), ") for lobby id", lobby_id)
            return []

        return rows[0]

    def get_level_info_from_name( self, scene_name ):
        """Gets list [min players and max players]"""

        query = "SELECT min_players, max_players " \
                "FROM levels " \
                "WHERE name = %s"

        rows = self.database.execute( query, [scene_name], fetch=True )

        if len(rows) != 1:
            DEBUG.LOGS.print("Did not receive exactly one result (count: ", len(rows), ") for scene name: ", scene_name)
            return []

        return rows[0]

    def get_lobby_target_scene_name( self, lobby_id ):
        """Gets the target scene name for the lobby id"""

        query = "SELECT levels.name " \
                "FROM levels " \
                "JOIN lobbies ON lobbies.level_id = levels.uid " \
                "WHERE lobbies.uid = %s"

        rows = self.database.execute( query, [lobby_id], fetch=True )

        if len(rows) != 1:
            DEBUG.LOGS.print("Did not receive exactly one result (count: ", len(rows), ") for lobby id", lobby_id)
            return []

        return rows[0][0]


    def join_lobby( self, client_id, lobby_id ):
        """ Joins game lobby

        :return: True if successful otherwise False
        """

        # check that the user can join the lobby
        query = "SELECT levels.max_players " \
                "FROM lobbies JOIN levels ON lobbies.level_id = levels.uid " \
                "WHERE (lobbies.game_id < 0 OR (lobbies.lobby_host_id >= 0 AND lobbies.game_id >= 0)) AND lobbies.uid = %s"

        lobby = self.database.execute( query, [lobby_id], fetch=True )
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
        """Removes lobby host from list of active lobby host"""

        self.database.remove_row( "lobby_host", ["host"], [host] )

    def select_lobby_by_game_host( self, game_host_id ):

        query = "SELECT lobby_host_id FROM lobbies WHERE game_id = %s"
        results =self.database.execute( query, [game_host_id], fetch=True )

        if len(results) == 0:
            return None
        else:
            return results[0][0]

    def remove_game_host( self, host ):
        """Removes game host from list of active games host"""

        self.database.remove_row( "games_host", ["host"], [host] )

    def add_game_host( self, host ):

        self.database.insert_row( "games_host", ["host"], [host] )

        return self.database.select_from_table( "games_host", ["uid"], ["host"], [host] )[0][0]

    def add_lobby_to_game_queue( self, lobby_id ):

        # check that the lobby does not already exist in the queue
        exist = self.database.select_from_table( "game_queue", ["COUNT(lobby_id)"], ["lobby_id"], [lobby_id] )[0][0] > 0

        if not exist:
            self.database.insert_row( "game_queue", ["lobby_id"], [lobby_id] )

    def remove_lobby_from_game_queue( self, lobby_id ):
        """Removes the lobby id from the que and resets the gmae id in lobbies"""
        self.database.remove_row("game_queue", ["lobby_id"], [lobby_id])
        # make sure that a game slot has not been assigned
        self.database.update_row("lobbies", ["game_id"], [-1], ["uid"], [lobby_id])

    def game_slot_assigned( self, lobby_id ):

        selected_lobby = self.database.select_from_table( "lobbies", ["game_id"], ["uid"], [lobby_id] )

        if len( selected_lobby ) > 0:
            return selected_lobby[0][0] > 0
        else:
            return False

    def get_available_game_slots( self ):
        """
        :return:    the first available game slot. if None, there is currently no slots.
        """

        # basicly select all game host that are not assigned to a lobby
        query = "SELECT games_host.uid, COUNT(lobbies.game_id) FROM games_host LEFT JOIN lobbies ON games_host.uid = lobbies.game_id GROUP BY games_host.uid HAVING COUNT(lobbies.game_id) = 0"

        rows = self.database.execute( query, [], fetch=True )

        if len( rows ) == 0:
            return None

        return rows[0]

    def get_client_game_id( self, reg_key ):

        query = "SELECT lobbies.game_id " \
                "FROM active_users " \
                "JOIN lobbies ON active_users.lobby_id = lobbies.uid " \
                "WHERE active_users.reg_key = %s "

        row = self.database.execute( query, [reg_key], fetch=True )

        if len( row ) != 1:
            return -1

        return row[0][0]

    def get_client_current_game_host( self, reg_key ):

        query = "SELECT games_host.host " \
                "FROM active_users " \
                "JOIN lobbies ON active_users.lobby_id = lobbies.uid " \
                "JOIN games_host ON games_host.uid = lobbies.game_id " \
                "WHERE active_users.reg_key = %s "

        row = self.database.execute( query, [ reg_key ], fetch=True )

        if len( row ) != 1:
            return -1

        return row[ 0 ][ 0 ]

    def get_game_host( self, game_id ):

        query = "SELECT host " \
                "FROM games_host " \
                "WHERE uid = %s"

        results = self.database.execute( query, [game_id], fetch=True )

        if len( results ) != 1:
            return None

        return results[0][0]

    def get_next_lobby_in_queue( self ):
        """Gets the next lobby id from the queue (removing it)"""

        query = "SELECT MIN(uid), lobby_id FROM game_queue"
        result = self.database.execute( query, [], fetch=True )

        if len(result) == 0 or result[0][0] is None:    # empty queue
            return None

        queued_lobby = result[0][1]

        # remove from queue
        query = "DELETE FROM game_queue WHERE lobby_id = %s"
        self.database.execute( query, [ queued_lobby ] )

        # make sure that the lobby still exist.
        # Should probably check it has enough players too
        query = "SELECT COUNT(UID) FROM lobbies WHERE uid = %s"
        result = self.database.execute( query, [queued_lobby], fetch=True )

        if result[0][0] > 0:
            return queued_lobby
        else:
            DEBUG.LOGS.print("Removed invalid lobby from que")
            return None

    def get_game_queue_size( self ):
        """Gets the size of the que"""

        query = "SELECT uid " \
                "FROM game_queue"

        rows = self.database.execute( query, [], fetch=True )

        #if len(rows) != 1:
        #    return -1

        return len(rows)

    def clear_game_host( self, game_id ):
        """Clears the game host for the lobbie"""

        self.database.update_row( "lobbies", ["game_id"], [-1], ["game_id"], [game_id] )

    def clear_users( self ):
        """removes all active users"""
        query = "DELETE FROM active_users"
        self.database.execute(query, [])


    def add_analytic_data( self, data_type, data, player_id, lobby_id, game_id, level_id, t ):
        DEBUG.LOGS.print(player_id,    lobby_id,   game_id,   level_id,   data_type,   data,   t)

        self.database.insert_row("analytics",
                                 ["player_id", "lobby_id", "game_id", "level_id", "data_type", "data", "time"],
                                 [player_id,    lobby_id,   game_id,   level_id,   data_type,   data,   t]
                                 )

    def debug( self ):

        users_query = "SELECT * FROM active_users"
        lobbies_query = "SELECT * FROM lobbies"
        game_query = "SELECT * FROM game_queue"
        lobby_host_query = "SELECT * FROM lobby_host"
        game_host_query = "SELECT * FROM games_host"
        levels_query = "SELECT * FROM levels"

        user_d = self.database.execute( users_query, [ ], fetch=True )
        lobbies_d = self.database.execute( lobbies_query, [ ], fetch=True )
        game_d = self.database.execute( game_query, [ ], fetch=True )
        lobbyh_d = self.database.execute( lobby_host_query, [ ], fetch=True )
        gameh_d = self.database.execute( game_host_query, [ ], fetch=True )
        levels_d = self.database.execute( levels_query, [ ], fetch=True )

        DEBUG.LOGS.print( "users", user_d )
        DEBUG.LOGS.print( "lobbies", lobbies_d )
        DEBUG.LOGS.print( "game que", game_d )
        DEBUG.LOGS.print( "lobbies host", lobbyh_d )
        DEBUG.LOGS.print( "games host", gameh_d )
        DEBUG.LOGS.print( "levels", levels_d )

    def debug_game_host( self ):

        game_host_query = "SELECT * FROM games_host"
        gameh_d = self.database.execute( game_host_query, [ ], fetch=True )
        DEBUG.LOGS.print( "games host", gameh_d )

    def debug_lobby_host( self ):

        lobby_host_query = "SELECT * FROM lobbies"
        lobbyh_d = self.database.execute( lobby_host_query, [ ], fetch=True )
        DEBUG.LOGS.print( "lobbies host", lobbyh_d )
