# this should be run once to setup the database,
# or whenever the database needs changing.
import time
import Common.DEBUG as DEBUG
import Common.sql_query as sql
import Common.Globals as Global
import mysql_setup_randomNames as randomNames
RUN_SQL_TEST = False


def setup():
    database = sql.sql_query( "tb_rpg", True )

    while not database.test_connection():

        time.sleep( 1 )  # try every second

    database.drop_table("analytics")
    database.drop_table("active_users")
    database.drop_table("lobbies")
    database.drop_table("lobby_host")
    database.drop_table("game_queue")
    database.drop_table("games_host")    #   // quick fix while we only support 1 host // TODO: fix
    database.drop_table("levels")

    database.add_table( "analytics", ["uid", "player_id", "lobby_id", "game_id",
                                      "level_id", "data_type", "data", "time" ],
                        [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                          "INT NOT NULL DEFAULT '-1'",
                          "INT NOT NULL DEFAULT '-1'",
                          "INT NOT NULL DEFAULT '-1'",
                          "INT NOT NULL DEFAULT '-1'",
                          "VARCHAR(10) NOT NULL",
                          "TEXT NOT NULL",
                          "INT NOT NULL DEFAULT '-1'"
                          ]
                        )

    database.add_table( "active_users", [ "uid", "nickname", "lobby_id", "reg_key" ],
                             [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                               "VARCHAR(255) NOT NULL",
                               "INT NOT NULL DEFAULT '-1'",
                               "VARCHAR(64) NOT NULL DEFAULT 'None'" ]
                             )

    database.add_table( "lobbies", [ "uid", "level_id", "game_id", "lobby_host_id", "game_count" ],
                             [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                               "INT NOT NULL DEFAULT '-1'",
                               "INT NOT NULL DEFAULT '-1'",
                               "INT NOT NULL DEFAULT '-1'",
                               "INT NOT NULL DEFAULT '0'" ]
                             )

    database.add_table( "lobby_host", ["uid", "host"],
                            [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                              "VARCHAR(16) NOT NULL DEFAULT '0.0.0.0'" ]
                            )

    database.add_table( "game_queue", ["uid", "lobby_id"],
                        [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                          "INT NOT NULL DEFAULT '-1'" ]
                        )

    database.add_table( "games_host", [ "uid", "host" ],
                             [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                               "VARCHAR(16) NOT NULL DEFAULT '0.0.0.0'" ]
                             )

    database.add_table( "levels", [ "uid", "name", "min_players", "max_players" ],
                             [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                               "VARCHAR(255) NOT NULL",
                               "INT NOT NULL DEFAULT '1'",
                               "INT NOT NULL DEFAULT '2'" ]
                             )

    database.insert_row("levels",
                        ["name", "min_players", "max_players"],
                        ["default", 2, 4]
                        )

    # set up the random name Database
    exist = database.add_table( "names_list_nouns", ["id", "word"],
                        ["INT UNSIGNED NULL AUTO_INCREMENT KEY",
                         "VARCHAR(255) NOT NULL"]
                        )[0] == 404

    if not exist:
        randomNames.add_nouns_to_database(database)

    exist = database.add_table( "names_list_adjective", [ "id", "word" ],
                        [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                          "VARCHAR(255) NOT NULL" ]
                        )[0] == 404

    if not exist:
        randomNames.add_adjective_to_database(database)

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