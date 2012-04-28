
import os
from MySQLdb import connect
from MySQLdb import cursors
import CASClient

import json, chat, sys
#import string
import datetime
from flask import Flask, request, render_template, redirect, session
app = Flask(__name__)

#used for sessions
app.secret_key = "J\"JOx[Lq\'.jt7P.qT5i\'"
app.permanent_session_lifetime = datetime.timedelta(7)
#app.permanent_session_lifetime = 30
app.session_cookie_name = "ISTREET_SESSION"
app.session_cookie_domain = "istreetsvr.heroku.com"

@app.route('/')
def index():
    netid = ""
    if 'username' in session:
        netid = session['username']
    return render_template('test.html', netid=netid)
    
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

@app.route('/eventslist', methods = ['GET'])
def eventsList():
    netid = ""
    response = authenticate()
    if(type(response) != str):
        return response #redirect
    else:
        netid = response
    return getJSONForQuery("select title, event_id, poster, name, time_start, time_end, description, entry, entry_description from pam_event, pam_club WHERE pam_club.club_id = pam_event.club_id AND DATE(time_start) > '2012-03-30'", "tigerapps")
#    return getJSONForQuery("select title, event_id, poster, name, time_start from pam_event, pam_club WHERE pam_club.club_id = pam_event.club_id AND DATE(time_start) <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) and time_start >= CURDATE() ORDER BY time_start", "tigerapps")

'''
@app.route('/eventinfo', methods = ['GET'])
def eventInfo():
    event_id = request.args.get("event_id")
    if event_id == None:
        return "Invalid request: missing event_id argument"

    return getJSONForQuery("select title, poster, event_id, time_start, time_end, description, entry, entry_description, name from pam_event, pam_club where pam_event.club_id = pam_club.club_id and event_id = " + str(event_id), "tigerapps")
'''

@app.route('/clubevents', methods = ['GET'])
def clubEvents():
    netid = ""
    response = authenticate()
    if(type(response) != str):
        return response #redirect
    else:
        netid = response
        
    name = request.args.get("name")
    if name == None:
        return "Invalid request: missing name argument"
    
    return getJSONForQuery("select title, event_id, poster, time_start, time_end, description, entry, entry_description, name from pam_event, pam_club where pam_event.club_id = pam_club.club_id and DATE(time_start) > '2012-03-30' and name = \"" + name + "\" ORDER BY time_start", "tigerapps")

    #return getJSONForQuery("select title, event_id, poster, time_start, time_end, description, entry, entry_description, name from pam_event, pam_club where pam_event.club_id = pam_club.club_id and time_start <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) and time_start >= CURDATE() and name = \"" + name + "\" ORDER BY time_start", "tigerapps")

@app.route('/clubslist', methods = ['GET'])
def clubsList():
    netid = ""
    response = authenticate()
    if(type(response) != str):
        return response #redirect
    else:
        netid = response
        
    return getJSONForQuery("select club_id, name from pam_club", "tigerapps")

def getJSONForQuery(query, database):
    cursor = sendQuery(query, database)
    table = getDictArrayForQueryResults(cursor)
    return str(json.dumps(table, encoding = "latin-1"))

def sendQuery(query, database):
    USE_PROD_SERVER = True
    host = ""
    user = ""
    passwd = ""
    
    if(USE_PROD_SERVER):
        host = 'www.tigerapps.org'
        user = 'iossvr24093'
        passwd = 'FpmMQe9MQRXgO63'
    else:
        host = 'dev.tigerapps.org'
        user = 'iossvrdev'
        passwd = 'development'

    connection = connect(host = host, user = user, passwd = passwd, db = database)
    cursor = connection.cursor(cursors.DictCursor)
    cursor.execute(query)
    
    return cursor

def getDictArrayForQueryResults(cursor):
    results = []
    row = cursor.fetchone()
    while row:
        for key in row:
            row[key] = str(row[key]) 
            '''necessary for things like datetime objects'''
        results.append(row)
        row = cursor.fetchone()
    return results

@app.route('/add', methods = ['POST'])
def add_message():
    netid = ""
    response = authenticate()
    if(type(response) != str):
        return response #redirect
    else:
        netid = response
    
    #TODO: what if the following two args dont exist?
    user_id = request.form['user_id']
    message = request.form['message']
    print user_id
    print message
    return chat.add(user_id, message)

@app.route('/get', methods = ['GET'])
def get_messages():
    netid = ""
    response = authenticate()
    if(type(response) != str):
        return response #redirect
    else:
        netid = response
        
    past = request.args.get("past")
    if past == None:
        past = ""
    return chat.get(past)

@app.route('/updateUser', methods = ['POST'])
def updateUser():
    netid = ""
    response = authenticate()
    if(type(response) != str):
        return response #redirect
    else:
        netid = response
        
    # GET
    fb_id = request.args.get("fb_id") #mandatory
    if fb_id == None:
        return "ERROR: missing fb_id parameter (HTTP GET)"
    
    # POST
    name = ""
    if(request.form.has_key("name")):
        name = request.form["name"]
    events = ""
    if(request.form.has_key("events")):
        events = request.form["events"]
        
    userCursor = sendQuery("SELECT * FROM user WHERE fb_id = \'" + fb_id + "\'", "istreet")
    theUser = userCursor.fetchone()
    
    if userCursor.fetchone():
        sys.stderr.write("ERROR: inconsistent server state: >1 user with given fb_id")
        return "ERROR: inconsistent server state - see error logs"
    
    if theUser:
        # set once for each of the three, if not ""
        if name != "":
            sendQuery("UPDATE user SET name = \'" + name + "\' WHERE fb_id = \'" + fb_id + "\'", "istreet")
        if events != "":
            sendQuery("UPDATE user SET events = \'" + events + "\' WHERE fb_id = \'" + fb_id + "\'", "istreet")
    else:
        # insert a new row with name, events, fbid, eventslist
        sendQuery(str.format("INSERT INTO user (name, events, fb_id) VALUES(\'{0}\', \'{1}\', \'{2}\')", name, events, fb_id), "istreet")

    return "SUCCESS"

@app.route('/attendEvent', methods = ['POST'])
def attendEvent():
    netid = ""
    response = authenticate()
    if(type(response) != str):
        return response #redirect
    else:
        netid = response
        
    # GET
    fb_id = request.args.get("fb_id")
    if fb_id == None:
        return "ERROR: missing fb_id parameter (HTTP GET)"
    
    # POST
    event_id = ""
    if(request.form.has_key("event_id")):
        event_id = request.form["event_id"]
        #TO DO: VALIDATE EVENT_ID
    else:
        return "ERROR: missing event_id parameter (HTTP POST)"
        
    userCursor = sendQuery("SELECT * FROM user WHERE fb_id = \'" + fb_id + "\'", "istreet")
    theUser = userCursor.fetchone()
    
    if not theUser:
        return "ERROR: no user with fb_id \'" + fb_id + "\' exists"

    if userCursor.fetchone():
        sys.stderr.write("ERROR: inconsistent server state: >1 user with given fb_id")
        return "ERROR: inconsistent server state - see error logs"    
    
    userEvents = theUser["events"]
    eventsArray = userEvents.split(", ")
    if not (event_id in eventsArray):
        eventsArray.append(event_id)
    newUserEvents = ", ".join(eventsArray)
    sendQuery(str.format("UPDATE user SET events = \'{0}\' WHERE fb_id = \'{1}\'", newUserEvents, fb_id), "istreet") 

    # send query to get row for user
    # extract events list and append event to events list
    # send query to update the row for that user with the new events list
    return "SUCCESS"

@app.route('/unattendEvent', methods = ['POST'])
def unattendEvent():
    netid = ""
    response = authenticate()
    if(type(response) != str):
        return response #redirect
    else:
        netid = response
        
    # GET
    fb_id = request.args.get("fb_id")
    if fb_id == None:
        return "ERROR: missing fb_id parameter (HTTP GET)"
    
    # POST
    event_id = ""
    if(request.form.has_key("event_id")):
        event_id = request.form["event_id"]
        #TO DO: VALIDATE EVENT_ID
    else:
        return "ERROR: missing event_id parameter (HTTP POST)"
        
    userCursor = sendQuery("SELECT * FROM user WHERE fb_id = \'" + fb_id + "\'", "istreet")
    theUser = userCursor.fetchone()
    
    if not theUser:
        return "ERROR: no user with fb_id \'" + fb_id + "\' exists"

    if userCursor.fetchone():
        sys.stderr.write("ERROR: inconsistent server state: >1 user with given fb_id")
        return "ERROR: inconsistent server state - see error logs"    
    
    userEvents = theUser["events"]
    eventsArray = userEvents.split(", ")
    if (event_id in eventsArray):
        eventsArray.remove(event_id)
    
    newUserEvents = ", ".join(eventsArray)
    sendQuery(str.format("UPDATE user SET events = \'{0}\' WHERE fb_id = \'{1}\'", newUserEvents, fb_id), "istreet") 

    # send query to get row for user
    # extract events list and remove event from events list
    # send query to update the row for that user with the new events list
    return "SUCCESS"

@app.route('/getUsersForEvent', methods = ['GET'])
def getUsersForEvent():
    netid = ""
    response = authenticate()
    if(type(response) != str):
        return response #redirect
    else:
        netid = response
        
    # GET
    event_id = request.args.get("event_id")
    if event_id == None:
        return "ERROR: missing event_id parameter (HTTP GET)"
    query = str.format("SELECT fb_id FROM user WHERE MATCH(events) AGAINST ('{0}' IN BOOLEAN MODE)", event_id)
    print query
    cursor = sendQuery(query, "istreet")
    
    row = cursor.fetchone()
    fb_ids = []
    while row:
        print "row!"
        fb_ids.append(row["fb_id"])
        row = cursor.fetchone()
    
    return ", ".join(fb_ids)

@app.route('/getEventsForUser', methods = ['GET'])
def getEventsForUser():
    netid = ""
    response = authenticate()
    if(type(response) != str):
        return response #redirect
    else:
        netid = response
        
    # GET
    fb_id = request.args.get("fb_id")
    if fb_id == None:
        return "ERROR: missing fb_id parameter (HTTP GET)"
    
    userCursor = sendQuery("SELECT * FROM user WHERE fb_id = \'" + fb_id + "\'", "istreet")
    theUser = userCursor.fetchone()
    
    if not theUser:
        return "ERROR: no user with fb_id \'" + fb_id + "\' exists"

    if userCursor.fetchone():
        sys.stderr.write("ERROR: inconsistent server state: >1 user with given fb_id")
        return "ERROR: inconsistent server state - see error logs"    
    
    return theUser["events"]

if __name__ == '__main__':
    if(len(sys.argv) > 1 and str.lower(sys.argv[1]) == "debug"):
        app.debug = True
        app.run()
    else:
        # Bind to PORT if defined, otherwise default to 5000.
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
