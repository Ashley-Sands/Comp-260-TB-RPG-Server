# this should be run once to setup the database,
# or whenever the database needs changing.
import time
import Common.DEBUG as DEBUG
import Common.sql_query as sql
import Common.Globals as Global

RUN_SQL_TEST = False


def setup():
    database = sql.sql_query( "tb_rpg", True )

    while not database.test_connection():

        time.sleep( 1 )  # try every second

    database.drop_table("games")    #   // quick fix while we only support 1 host // TODO: fix

    database.add_table( "active_users", [ "uid", "nickname", "lobby_id", "reg_key" ],
                             [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                               "VARCHAR(255) NOT NULL",
                               "INT NOT NULL DEFAULT '-1'",
                               "VARCHAR(64) NOT NULL DEFAULT 'None'" ]
                             )

    database.add_table( "lobbies", [ "uid", "level_id", "game_id" ],
                             [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                               "INT NOT NULL DEFAULT '-1'",
                               "INT NOT NULL DEFAULT '-1'" ]
                             )

    database.add_table( "games", [ "uid", "available", "host" ],
                             [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                               "BOOL NOT NULL DEFAULT TRUE",
                               "VARCHAR(16) NOT NULL DEFAULT '0.0.0.0'" ]
                             )

    database.add_table( "levels", [ "uid", "name", "min_players", "max_players" ],
                             [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                               "VARCHAR(255) NOT NULL",
                               "INT NOT NULL DEFAULT '1'",
                               "INT NOT NULL DEFAULT '2'" ]
                             )

    DEBUG.LOGS.print( "Database Setup Finished!" )

    if RUN_SQL_TEST:
        mysql_test()


def mysql_test():
    pass

if __name__ == "__main__":

    DEBUG.LOGS.init()
    Global.setup()

    setup()
    mysql_test()

    DEBUG.LOGS.print("SQL Setup complete")
    time.sleep(2)

    DEBUG.LOGS.close()
    print("Bey bey!")