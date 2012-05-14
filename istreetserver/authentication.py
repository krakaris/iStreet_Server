from istreetserver import app

from flask import request, session, Response
import CASClient

from functools import wraps
import string, random

def requires_CASauth(f):
    '''
    Defines a wrapper for URLs that require CAS authorization.
    '''
    @wraps(f)
    def decorated(*args, **kwargs):
        netid = ""
        response = authenticate()
        if(type(response) != str): # if response is a netid
            return response #redirect
        else:
            netid = response
            args = (netid, )
            return f(*args, **kwargs)
    return decorated

def authenticate():
    '''
    Returns the netid if the user has a session cookie, or a CAS redirect response otherwise.
    '''
    if 'username' in session:
        print "cookied in!"
        return str(session['username'])
    else:
        return CASLogin()

def CASLogin():
    '''
    Returns the netid if the URL has a valid CAS-issued ticket, or a CAS redirect response otherwise.
    '''
    ticket = ""
    if(request.args.has_key("ticket")):
        ticket = request.args.get("ticket")
    C = CASClient.CASClient()
    response = C.Authenticate(ticket)
    if(type(response) != str):
        return response #redirect
    else:
        # create / confirm the existence of a cookie with the right netid
        session['username'] = response
        session.permanent = True
        return response


@app.route('/login', methods = ['GET'])
@requires_CASauth
def login(netid):
    '''
    Returns SUCCESS: <netid> (only after successful CAS authorization, but this is the case everywhere with the @require_CASauth decorator)
    '''
    return "SUCCESS: " + netid

@app.route('/logout', methods = ['GET'])
def logout():
    '''
    Logs the user out by removing the session cookie. Returns "SUCCESS".
    '''
    # remove the username from the session if it's there
    session.pop('username', None)
    return "SUCCESS"

import hashlib

def check_auth(username, password):
    '''
    Returns true if the user's credentials are valid through challenge-response authentication, false otherwise.
    '''
    PRIVATE_KEY = "q{4fI&druS9Rz:)!o@0i"
    challenge = session['challenge'];
    expected_response = hashlib.md5(challenge + PRIVATE_KEY).hexdigest()
    success = (password == expected_response)
    if not success:
        print "UH OH!"
    else:
        print "success!"
    return password == expected_response

def CR_authentication():
    """Sends a 401 response for challenge-response authorization"""
    
    # create a random 10 character string
    choices = string.letters + string.digits + string.punctuation;
    randomString = ''.join(random.choice(choices) for i in range(10))
    session['challenge'] = randomString
 
    return Response('Access failed.', 401, {'WWW-Authenticate': str.format('Basic realm=\"Protected iStreet event data; Challenge: {0}\"', randomString)})

def requires_CRauth(f):
    '''
    Defines a wrapper for URLs that require challenge-response authorization.
    '''
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return CR_authentication()
        return f(*args, **kwargs)
    return decorated
