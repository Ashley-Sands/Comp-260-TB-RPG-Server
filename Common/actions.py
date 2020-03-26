import Common.DEBUG as DEBUG

def process_client_identity( message_obj ):

    DEBUG.LOGS.print("Recivedd id", message_obj["client_id"], message_obj["reg_key"] )

    from_conn = message_obj.from_connection
    # add the clients data to the connection
    from_conn.set_client_key( message_obj["client_id"], message_obj["reg_key"] )
    from_conn.client_nickname = message_obj["nickname"]