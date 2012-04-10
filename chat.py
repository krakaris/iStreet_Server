import os
from MySQLdb import connect, cursors, escape_string

import app

def add(user_id, message):
    query = "INSERT INTO chatitems VALUES (null, null, \'" + escape_string(user_id) + "\', \'" + escape_string(message) + "\')"
    app.sendQuery(query, "istreet")
    return ""


'''returns JSON string with id, added (timestamp), user_id, and message'''
def get(past):
    if (past != ""):
        return app.getJSONForQuery("SELECT * FROM chatitems WHERE id > " + escape_string(past) + " ORDER BY added LIMIT 50", "istreet")
    else:
        return app.getJSONForQuery("SELECT * FROM chatitems ORDER BY added LIMIT 50", "istreet")
