from istreetserver import app

from flask import request, session, Response
from database import sendQuery
import CASClient

from functools import wraps
import string, random

def requires_CASauth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        netid = ""
        response = authenticate()
        if(type(response) != str):
            return response #redirect
        else:
            netid = response
            args = (netid, )
            return f(*args, **kwargs)
    return decorated

# returns netid or redirect object
def authenticate():
    if 'username' in session:
        print "cookied in!"
        return str(session['username'])
    else:
        return CASLogin()

# returns netid or redirect object
def CASLogin():
    ticket = ""
    if(request.args.has_key("ticket")):
        ticket = request.args.get("ticket")
    C = CASClient.CASClient()
    response = C.Authenticate(ticket)
    if(type(response) != str):
        return response #redirect
    else:
        # create / confirm the existence of a cookie
        session['username'] = response
        session.permanent = True
        return response


@app.route('/login', methods = ['GET'])
@requires_CASauth
def login(netid):
    ''''''
    '''cursor = sendQuery("SELECT * FROM user WHERE netid = \'" + netid + "\'", "istreet")
    theUser = cursor.fetchone()
    if theUser == None:
        sendQuery(str.format("INSERT INTO user (netid, name, fb_id, events, loggedin) VALUES(\'{0}\', \'\', \'\', \'\', 1)", netid), "istreet")
    else:
        if theUser["loggedin"] != 0:
            session.pop('username', None)
            return "ERROR: user logged in on another device."
        else:
            sendQuery("UPDATE user SET loggedin = 1 WHERE netid = \'" + netid + "\'", "istreet")
    '''
    
    return "SUCCESS: " + netid

@app.route('/logout', methods = ['GET'])
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    #if netid != None:
    #    sendQuery("UPDATE user SET loggedin = 0 WHERE netid = \'" + netid + "\'", "istreet")
    return "SUCCESS"

import hashlib

def check_auth(username, password):
    PRIVATE_KEY = "q{4fI&druS9Rz:)!o@0i"
    challenge = session['challenge'];
    expected_response = hashlib.md5(challenge + PRIVATE_KEY).hexdigest()
    return password == expected_response

def CR_authentication():
    """Sends a 401 response for challenge-response authorization"""
    # create a random 10 character string
    choices = string.letters + string.digits + string.punctuation;
    randomString = ''.join(random.choice(choices) for i in range(10))
    session['challenge'] = randomString
 
    return Response('Access failed.', 401, {'WWW-Authenticate': str.format('Basic realm=\"Protected iStreet event data; Challenge: {0}\"', randomString)})

def requires_CRauth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return CR_authentication()
        return f(*args, **kwargs)
    return decorated
