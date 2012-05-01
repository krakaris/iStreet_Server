from istreetserver import app

from flask import request, render_template, redirect, session, Response
import CASClient

from functools import wraps
import string, random


@app.route('/login', methods = ['GET'])
def login():
    response = authenticate()
    if(type(response) != str):
        return response
    else:
        return "SUCCESS: " + response

@app.route('/logout', methods = ['GET'])
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return "SUCCESS"

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

def requires_CASauth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print "checking authorization from decorated"
        netid = ""
        response = authenticate()
        if(type(response) != str):
            return response #redirect
        else:
            netid = response
            args = args + (netid, )
            return f(*args, **kwargs) # netid = netid)
    return decorated

import hashlib

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    PRIVATE_KEY = "q{4fI&druS9Rz:)!o@0i"
    challenge = session['challenge'];
    m = hashlib.md5(challenge + PRIVATE_KEY)
    print "received: " + password
    expected_response = m.hexdigest()
    #return password == "password"
    return password == expected_response

def CR_authentication():
    """Sends a 401 response for challenge-response authorization"""
    # create a random 10 character string
    choices = string.letters + string.digits + string.punctuation;
    randomString = ''.join(random.choice(choices) for i in range(10))
    #randomString = "0123456789"
    session['challenge'] = randomString
    print "sending challenge: " + randomString
    
    PRIVATE_KEY = "q{4fI&druS9Rz:)!o@0i"
    m = hashlib.md5(randomString + PRIVATE_KEY)
    expected_response = m.digest()
    print "expected unencoded: " + (randomString + PRIVATE_KEY)
    print "expecting: " + expected_response
    print ""
    return Response('Access failed.', 401, {'WWW-Authenticate': str.format('Basic realm=\"Protected iStreet event data; Challenge: {0}\"', randomString)})

def requires_CRauth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print "checking authorization from decorated"
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return CR_authentication()
        return f(*args, **kwargs)
    return decorated
