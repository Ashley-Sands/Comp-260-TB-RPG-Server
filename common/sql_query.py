import sqlite3
import mysql.connector
import mysql_helpers
from Globals import Global
from Globals import GlobalConfig as Config
import os, os.path
import re  # regex
import random

class sql_query():

    def __init__(self, db_name, using_mysql=False):

        self.using_mysql = using_mysql
        self.db_name = db_name

        self.connection = None
        self.cursor = None

        # make sure that the db root is set
        if not Config.is_set( "db_root" ):
            Config.set("db_root", "")

        # if using MYSQL make sure that the user has set a host, username and password!
        if self.using_mysql:
            if not Config.is_set( "mysql_host"):
                Config.set("mysql_host", "localhost")

            if not Config.is_set( "mysql_user" ):
                Config.set("mysql_user", "root")

            if not Config.is_set( "mysql_pass" ):
                Config.set("mysql_pass", "")  # please set a password in some other file (that is not synced with public version control)

            print( "mysql details:", Config.get("mysql_host"), Config.get("mysql_user"), "*" * random.randint( 6, 16 ), db_name )

    def connect_db(self):
        """ Connect to the SQLite DB, creates new if not exist """

        if self.connection is not None:
            return

        if self.using_mysql:
            self.connection, self.cursor = mysql_helpers.MySqlHelpers.mysql_connect(
                                                                                    Config.get("mysql_host"),
                                                                                    Config.get("mysql_user"),
                                                                                    Config.get("mysql_pass"),
                                                                                    self.db_name )
        else:
            self.connection = sqlite3.connect( Config.get("db_root")+self.db_name )
            self.cursor = self.connection.cursor()

    def destroy_database(self):

        if not self.using_mysql:
            if os.path.exists( Config.get("db_root")+self.db_name ):
                os.remove( Config.get("db_root")+self.db_name )
        else:
           mysql_helpers.MySqlHelpers.mysql_destroy_database( Config.get("mysql_host"),
                                                              Config.get("mysql_user"),
                                                              Config.get("mysql_pass"),
                                                              self.db_name )


    def close_db(self, commit = True):
        """Closes the db connection"""

        # check that the connection exists
        if self.connection is None and self.cursor is None:
            return

        #if not self.using_mysql and commit:
        if commit:
            self.connection.commit()

        # in mysql we must close the cursor and connection
        if self.using_mysql:
            self.cursor.close()

        self.connection.close()

        # reset the connection to insure we established a new connection
        self.connection = None
        self.cursor = None

    def get_all_tables(self, close_conn = True):
        """ Gets an list of tuples with all table names in database

        :return: list of table names [table_name, ...]
        """
        if self.using_mysql:
            query = "SHOW TABLES"
        else:
            query = "SELECT name FROM sqlite_master WHERE type='table'"

        self.connect_db()

        self.cursor.execute(query)
        data = self.cursor.fetchall()

        # get only the table names
        data = [ r[0] for r in data ]

        if close_conn:
            self.close_db()

        return data

    def get_table_columns(self, table_name):
        """ Gets a list of tuples with all column data for table

        :param table_name:  table to get column data from
        :return:            (sqlite) [(col_id, col_name, type, can_be_null, default_value, part_of_primary_key)...]
                            (mysql) [(type, null, key, default, extra)...]
        """

        table_name = re.sub("\s", "_", table_name ) # replace white space with underscores

        if self.using_mysql:
            query = "DESCRIBE "+table_name
        else:
            query = "pragma table_info("+table_name+")"

        self.connect_db()

        try:
            self.cursor.execute(query)
            data = self.cursor.fetchall()
        except Exception as e:
            print(e)
            data = []

        self.close_db()

        return data

    def get_table_column_names(self, table_name):
        """ Gets a list of all column names (in order)"""

        table_name = re.sub("\s", "_", table_name)  # replace white space with underscores

        if self.using_mysql:
            return [u[0] for u in self.get_table_columns(table_name)]
        else:
            return [u[1] for u in self.get_table_columns(table_name)]

    def table_exist(self, table_name, close_connect = True):
        """Check if table exist in database"""

        tables = self.get_all_tables()

        return table_name in tables

    ''' Check if table exist else creats it.
    @:param table_name: Name of the table to be created.
    @:param col_names: col string
    '''
    def add_table(self, table_name, col_names, data_types, data_lengths=None, default_values=None):
        """Adds new table to database

        :param col_names:       List of column names
        :param data_types:      list of data types (must match col names or none)
        :param data_lengths:    list of max column length (must match col names or none)
        :param default_values:  list of default values for column (must match col names or none)
        """

        table_name = re.sub("\s", "_", table_name)  # replace white space with underscores

        if self.table_exist( table_name ):
            print("Error: can not create table(", table_name, "), already exist")
            return 404, "table already exist"

        query = "CREATE TABLE "+table_name
        columns = []

        for i, v in enumerate(col_names):
            data_l = ""
            default_v = ""

            if data_lengths is not None and data_lengths[i] != "":
                data_l = "("+data_lengths[i]+")"

            if default_values is not None and default_values[i] != "":
                if self.using_mysql:
                    default_v = '"'+default_values[i]+'"'
                else:
                    default_v = ' DEFAULT "'+default_values[i]+'"'

            v = re.sub("\s", "_", v )  # replace white space with underscores

            # make sure the first character is not a number
            failed = False
            try:
                int(v[0])
            except: # add underscore at start if it does
                failed = True

            if not failed:
                v = "_"+v

            columns.append( v +" "+ data_types[i] + data_l + default_v )

        print(columns)
        columns = ', '.join(columns)

        self.connect_db()

        query += " ("+columns+")"
        print(query)
        self.cursor.execute(query)

        self.close_db()

        print("Table Created")
        return None

    def drop_table(self, table_name):
        """drops table from database"""
        if not self.table_exist( table_name ):
            print("Error: can not drop", table_name,"table, does not already exist")
            return

        self.connect_db()

        query = "DROP TABLE " + table_name
        self.cursor.execute(query)

        self.close_db()

        print(table_name, "Droped")

    def insert_row(self, table_name, value_columns, value_data):
        """Inserts rot into table"""
        if not self.table_exist(table_name):
            print("Error: can not insert row into table, table does not exist")
            return

        self.connect_db()

        if self.using_mysql:
            val_str = "%s"
        else:
            val_str = "?"

        col_name_str = ', '.join(value_columns)
        col_value_str = ', '.join([val_str] * len(value_data))

        query = "INSERT INTO " + table_name + " (" + col_name_str + ") VALUES (" + col_value_str + ") "
        print(query, value_data)
        if Global.DEBUG:
            print("query: ", query, "Data", value_data)

        self.cursor.execute(query, value_data)

        self.close_db()

        print("data Inserted to table")

    def remove_row(self, table_name, where_columns, where_data):
        """remove row from table"""
        if not self.table_exist(table_name):
            print("Error: can not delete row from table, table does not exist")
            return

        where_str = self.sql_string_builder( where_columns, "AND " )

        self.connect_db()

        query = " DELETE FROM "+table_name+" WHERE "+where_str

        if Global.DEBUG:
            print(query, where_data)

        self.cursor.execute( query, where_data )

        self.close_db()

    def select_from_table(self, table_name, column_names, where_columns=[], where_data=[], order_data={}):
        """ Selects rows of data from table

        :param table_name:      Name of table to select data from
        :param column_names:    list of column names to get data rom (* = all)
        :param where_columns:   list of where column names
        :param where_data:      list of where data (must match where column order)
        :param order_data:      dict of order data keys {"order_columns": list of strings, "sort_type": string (ASC || DESC)}
        :return:
        """
        if not self.table_exist(table_name):
            print("Error: can not select from table, table does not exist")
            return

        # turn the lists of column names into a usable sql string
        col_str = self.sql_string_builder( column_names, ",", False )
        where_str = self.sql_string_builder(where_columns, "AND ")

        # create the where string
        if len(where_columns) > 0:
            where_str = " WHERE "+where_str
        else:
            where_str = ""

        # create the order by string
        if order_data is not None and "order_columns" in order_data and \
                "sort_type" in order_data and type(order_data["order_columns"] is list):
            order_str = ', '.join(order_data["order_columns"])
            order_str = "ORDER BY " + order_str + " " + order_data["sort_type"]
        else:
            order_str = ""

        query = "SELECT " + col_str + " FROM " + table_name + where_str + order_str

        print (query)
        self.connect_db()
        self.cursor.execute( query, where_data )
        data = self.cursor.fetchall()

        self.close_db()

        return data

    def update_row(self, table_name, set_columns, set_data, where_columns, where_data ):
        """ Updates table row

        :param table_name:      Name of table to update
        :param set_columns:     list or tuple of columns to set
        :param set_data:        list or tuple of data to set into columns (order must match set_str)
        :param where_columns:   list or tuple of wheres
        :param where_data:      list or tuple of where data (order must match where_str)
        :return:
        """
        if not self.table_exist(table_name):
            print("Error: can not update row in table, table does not exist")
            return

        set_str = self.sql_string_builder(set_columns, ",")
        where_str = self.sql_string_builder(where_columns, "AND ")
        data = (*set_data, *where_data)

        self.connect_db()

        query = "UPDATE "+table_name+" SET "+set_str+" WHERE "+where_str

        print( query )

        self.cursor.execute(query, data)

        self.close_db()

    def sql_string_builder(self, column_names, join, add_equals=True):
        """ build a list of column names in to sql query string for set and where ect... """

        if self.using_mysql:
            str_val = "%s"
        else:
            str_val = "?"

        string = ""
        if add_equals is True:
            equals = "={0} ".format(str_val)
        else:
            equals = " "

        # make column string
        for s in column_names:
            string += s + equals + join

        # clear end ','
        if string[-len(join):] == join:
            string = string[:-len(join)]

        return string

