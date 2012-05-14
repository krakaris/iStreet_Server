from istreetserver import app

from MySQLdb import escape_string
from authentication import requires_CASauth, requires_CRauth
from flask import request
from database import sendQuery, getJSONForQuery

@app.route('/add', methods = ['POST'])
@requires_CASauth
@requires_CRauth
def add_message(netid):
    '''
    Adds a message to the chat system by adding it to the database. Returns an empty string.
    '''
    if not request.form.has_key("message"):
        return ""
    
    message = request.form['message']

    query = "INSERT INTO chatitems VALUES (null, null, %s, %s)"
    database = "istreet"
    params = (netid, message)
    sendQuery(query, database, params = params)
    
    return ""

@app.route('/get', methods = ['GET'])
@requires_CASauth
def get_messages(netid):
    '''
    Returns the most recent 50 messages in the chat database in JSON.
    '''
   
    past = request.args.get("past")

    if (past == None):
        past = "-1"
        
    try:
        p = int(past)
    except ValueError:
        return "Nice try! No funky SQL injection attacks in my territory!"
    query = "SELECT * FROM chatitems WHERE id > %s ORDER BY added DESC LIMIT 50"
    database = "istreet"
    params = (p, )
    return getJSONForQuery(query, database, params = params)
