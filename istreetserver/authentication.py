from istreetserver import app

from flask import request, render_template, redirect, session
import CASClient

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
