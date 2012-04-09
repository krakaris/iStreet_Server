import os
from MySQLdb import connect
from MySQLdb import cursors

import app

def add(user_id, message):
    app.sendQuery("INSERT INTO chatitems VALUES (null, null, '" + MySQLdb.escape_string(user_i\
d) + "', '" + MySQLdb.escape_string(message) + "'", "istreet")

def get(past):
    if (past != ""):
        return app.getJSONForQuery("SELECT * FROM chatitems WHERE id > " + MySQLdb.escape_string(past) + " ORDER BY added LIMIT 50", "istreet")
     else:
        return app.getJSONForQuery("SELECT * FROM chatitems ORDER BY added LIMIT 50", "istreet")
