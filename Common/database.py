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

    def get_lobby_host_ids( self, lobby_id ):
        """ gets the lobby host id and game host id (tuple)"""
        query = "SELECT lobby_host_id, game_id " \
                "FROM lobbies " \
                "WHERE uid = %s"

        results = self.database.execute( query, [lobby_id] )

        if len( results ) != 1:
            return -1, -1

        return results[0]

    def get_lobby_host( self, host_id ):

        query = "SELECT host " \
                "FROM lobby_host " \
                "WHERE uid=%s"

        host = self.database.execute(query, [host_id])
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

    def update_lobby_host( self, lobby_id ):
        pass

    def update_lobby_game_host ( self, lobby_id, game_host_id ):
        """ updates the lobbies game host removeing it from the game que"""

        self.database.update_row( "lobbies", ["game_id"], [game_host_id], ["uid"], [lobby_id])
        self.database.remove_row("game_queue", ["lobby_id"], [lobby_id])


    def clear_lobby_host( self, lobby_id ):

        self.database.update_row( "lobbies", ["lobby_host_id"], [-1], ["uid"], [lobby_id])

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

    def get_lobby_info( self, lobby_id ):
        """Gets list [Level name, min players and max players]"""

        query = "SELECT levels.name, levels.min_players, levels.max_players " \
                "FROM levels " \
                "JOIN lobbies ON lobbies.level_id = levels.uid " \
                "WHERE lobbies.uid = %s"

        rows = self.database.execute( query, [lobby_id] )

        if len(rows) != 1:
            DEBUG.LOGS.print("Did not receive exactly one result (count: ", len(rows), ") for lobby id", lobby_id)
            return []

        return rows[0]

    def get_lobby_target_scene_name( self, lobby_id ):
        """Gets the target scene name for the lobby id"""

        query = "SELECT levels.name " \
                "FROM levels " \
                "JOIN lobbies ON lobbies.level_id = levels.uid " \
                "WHERE lobbies.uid = %s"

        rows = self.database.execute( query, [lobby_id] )

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
        print(self.database.select_from_table( "lobbies", ["game_id"], ["uid"], [lobby_id] )[0][0])
        return self.database.select_from_table( "lobbies", ["game_id"], ["uid"], [lobby_id] )[0][0] > 0

    def get_available_game_slots( self ):
        """
        :return:    the first available game slot. if None, there is currently no slots.
        """

        # basicly select all game host that are not assigned to a lobby
        query = "SELECT games_host.uid, COUNT(lobbies.game_id) FROM games_host LEFT JOIN lobbies ON games_host.uid = lobbies.game_id GROUP BY games_host.uid HAVING COUNT(lobbies.game_id) = 0"

        rows = self.database.execute( query, [] )

        if len( rows ) == 0:
            return None

        return rows[0]


    def get_client_game_id( self, reg_key ):

        query = "SELECT lobbies.game_id " \
                "FROM active_users " \
                "JOIN lobbies ON active_users.lobby_id = lobbies.uid " \
                "WHERE active_users.reg_key = %s "

        row = self.database.execute( query, [reg_key] )

        if len( row ) != 1:
            return -1

        return row[0][0]

    def get_client_current_game_host( self, reg_key ):

        query = "SELECT games_host.host " \
                "FROM active_users " \
                "JOIN lobbies ON active_users.lobby_id = lobbies.uid " \
                "JOIN games_host ON games_host.uid = lobbies.game_id " \
                "WHERE active_users.reg_key = %s "

        row = self.database.execute( query, [ reg_key ] )

        if len( row ) != 1:
            return -1

        return row[ 0 ][ 0 ]

    def get_game_host( self, game_id ):

        query = "SELECT host " \
                "FROM games_host " \
                "WHERE uid = %s"

        results = self.database.execute( query, [game_id] )

        if len( results ) != 1:
            return None

        print("Get Client Host results >>>>>>>>>>>>>>>>>>>>>>>>> ", results)

        return results[0][0]

    def get_next_lobby_in_queue( self ):
        """Gets the next lobby id from the que"""

        query = "SELECT MIN(uid), lobby_id FROM game_queue"
        result = self.database.execute( query, [] )

        if len(result) == 0:
            return None

        return result[0][1]

    def get_game_queue_size( self ):
        """Gets the size of the que"""

        query = "SELECT uid " \
                "FROM game_queue"

        rows = self.database.execute( query, [] )

        #if len(rows) != 1:
        #    return -1

        return len(rows)
