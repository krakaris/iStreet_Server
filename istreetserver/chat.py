from istreetserver import app

from MySQLdb import escape_string
from authentication import requires_CASauth
from flask import request
from database import sendQuery, getJSONForQuery

@app.route('/add', methods = ['POST'])
@requires_CASauth
def add_message(netid):
    
    #TODO: default to netid, use user_id if there is one.
    user_id = request.form['user_id']
    
    #TODO: what if the following two args dont exist?

    message = request.form['message']
    
    query = "INSERT INTO chatitems VALUES (null, null, \'" + escape_string(user_id) + "\', \'" + escape_string(message) + "\')"
    sendQuery(query, "istreet")

    return ""

@app.route('/get', methods = ['GET'])
@requires_CASauth
def get_messages(netid):
   
    past = request.args.get("past")

    if (past == None):
        past = "-1"
    return getJSONForQuery("SELECT * FROM chatitems WHERE id > " + escape_string(past) + " ORDER BY added DESC LIMIT 50", "istreet")
