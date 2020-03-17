import common.sql_query as sql
import DEBUG

class Database:

    def __init__( self ):

        # make sure that the database has been set up
        self.database = sql.sql_query("tb_rpg", True)

        self.database.add_table( "active_users", ["uid", "nickname", "lobby_id", "game_id"],
                                 ["INT UNSIGNED NULL AUTO_INCREMENT KEY", "VARCHAR(255) NOT NULL",
                                  "INT NOT NULL DEFAULT '-1'", "INT NOT NULL DEFAULT '-1'"]
                                 )

        DEBUG.DEBUG.print( "Database Inited Successfully!" )
