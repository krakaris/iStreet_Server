from istreetserver import app

from flask import request
from authentication import requires_CRauth, requires_CASauth
from database import sendQuery

import json


@app.route('/updateUser', methods = ['POST'])
@requires_CASauth
@requires_CRauth
def updateUser(netid):
    """
    Create/update the user defined by netid (obtained from session cookie).
    
    Parameters:
    fb_id: HTTP POST (optional) (ex. fb_id=88888888 or "fb_id=" to disassociate the netid and fb_id)
    name: HTTP POST (optional) (ex. "name=Rishi%20Narang)
    
    A single netid only has one fb_id, and an fb_id can only be used for a single netid.
    If there is already a netid linked to the given fb_id, an error message is returned.
    Returns "SUCCESS" otherwise.
    Note: "fb_id=" should be used as a parameter when a user logs out of facebook in the app.
    """
    
    fb_id = None
    if request.form.has_key("fb_id"):
        fb_id = request.form.get("fb_id")
        if(len(fb_id) > 0):
            # see if there are any other netids associated with that fb_id
            query = "SELECT * FROM user WHERE fb_id = %s AND netid != %s"
            database = "istreet"
            params = (fb_id, netid)
            fbUsers = sendQuery(query, database, params = params)
            if(fbUsers.fetchone()):
                return "Error: user with given fb_id already exists"
    
    name = None
    if(request.form.has_key("name")):
        name = request.form["name"]
    
    query = "SELECT * FROM user WHERE netid = %s"
    database = "istreet"
    params = (netid, )
    userCursor = sendQuery(query, database, params = params)
    theUser = userCursor.fetchone()
    
    if theUser:
        if fb_id != None:
            query = "UPDATE user SET fb_id = %s WHERE netid = %s"
            params = (fb_id, netid)
            sendQuery(query, database, params = params)
            
        if name != None:
            query = "UPDATE user SET name = %s WHERE netid = %s"
            params = (name, netid)
            sendQuery(query, database, params = params)
    else:
        if fb_id == None:
            fb_id = ""
        if name == None:
            name = ""
        
        query = "INSERT INTO user (netid, name, fb_id, events) VALUES(%s, %s, %s, %s)"
        params = (netid, name, fb_id, "")
        sendQuery(query, database, params = params)

    return "SUCCESS"

@app.route('/attendEvent', methods = ['POST'])
@requires_CASauth
@requires_CRauth
def attendEvent(netid):
    """
    Add an event to the list of events for the user (defined by netid, which is obtained from session cookie).
    
    Parameters:
    event_id: HTTP POST (required) (ex. event_id=105)
    
    If the user has already added that event, nothing changes. 
    Creates the user if the user has not yet been created in the database.
    Returns an error message if the event_id parameter is missing, returns "SUCCESS" otherwise.
    """
    event_id = ""
    if(request.form.has_key("event_id")):
        event_id = request.form["event_id"]
        #TO DO: VALIDATE EVENT_ID?
    else:
        return "ERROR: missing event_id parameter (HTTP POST)"
        
    query = "SELECT * FROM user WHERE netid = %s"
    database = "istreet"
    params = (netid, )
    userCursor = sendQuery(query, database, params = params)
    theUser = userCursor.fetchone()
    
    userEvents = ""
    if theUser == None:
        query = "INSERT INTO user (netid, name, fb_id, events) VALUES(%s, %s, %s, %s)"
        params = (netid, "", "", "")
        sendQuery(query, database, params = params)
    else:
        userEvents = theUser["events"]
    
    if userEvents == None or userEvents == "":
        eventsArray = []
    else:
        eventsArray = userEvents.split(", ")
    
    if not (event_id in eventsArray):
        eventsArray.append(event_id)
    
    newUserEvents = ", ".join(eventsArray)
    query = "UPDATE user SET events = %s WHERE netid = %s"
    params = (newUserEvents, netid)
    sendQuery(query, database, params = params) 

    return "SUCCESS"

@app.route('/unattendEvent', methods = ['POST'])
@requires_CASauth
@requires_CRauth
def unattendEvent(netid):
    """
    Remove an event from the list of events for the user (defined by netid, which is obtained from session cookie).
    
    Parameters:
    event_id: HTTP POST (required) (ex. event_id=105)
    
    If the event is not on the user's list of events, nothing changes. 
    If the user has not yet been created in the database, nothing changes.
    Returns an error message if the event_id parameter is missing, returns "SUCCESS" otherwise.
    """
    
    event_id = ""
    if(request.form.has_key("event_id")):
        event_id = request.form["event_id"]
        #TO DO: VALIDATE EVENT_ID
    else:
        return "ERROR: missing event_id parameter (HTTP POST)"
        
    query = "SELECT * FROM user WHERE netid = %s"
    database = "istreet"
    params = (netid, )
    userCursor = sendQuery(query, database, params = params)    
    theUser = userCursor.fetchone()
    
    if theUser == None:
        return "SUCCESS"

    userEvents = theUser["events"]
    eventsArray = userEvents.split(", ")
    if (event_id in eventsArray):
        eventsArray.remove(event_id)
    
    newUserEvents = ", ".join(eventsArray)
    query = "UPDATE user SET events = %s WHERE netid = %s"
    params = (newUserEvents, netid)
    sendQuery(query, database, params = params) 

    return "SUCCESS"

@app.route('/getUsersForEvent', methods = ['GET'])
@requires_CASauth
@requires_CRauth
def getUsersForEvent(netid):
    """
    Get the users (a list of fb_id's) attending the event.
    
    Parameters:
    event_id: HTTP GET (required) (ex. fb_id=88888888)
    
    Returns the list of fb_id's for users attending that event (only users with fb_id's are included).
    """
    
    event_id = request.args.get("event_id")
    if event_id == None:
        return "ERROR: missing event_id parameter (HTTP GET)"
    
    query = "SELECT fb_id FROM user WHERE (events REGEXP %s or events REGEXP %s or events REGEXP %s) AND (fb_id IS NOT NULL AND fb_id != %s)"
    database = "istreet"
    params = (str.format("^{0}, ", event_id), str.format(", {0}, ", event_id), str.format(", {0}$", event_id), "")
    cursor = sendQuery(query, database, params = params)    
    
    row = cursor.fetchone()
    fb_ids = []
    while row:
        fb_ids.append(row["fb_id"])
        row = cursor.fetchone()
    
    return ", ".join(fb_ids)

@app.route('/getEventsForUser', methods = ['GET'])
@requires_CASauth
@requires_CRauth
def getEventsForUser(netid):
    """
    Get the events that the user, defined by the fb_id,  is attending.
    If no fb_id is provided, get the events that the user making the call (netid from session cookie) is attending.
    
    Parameters:
    fb_id: HTTP GET (optional) (ex. fb_id=88888888)
    
    Returns the list of events that the user is attending, or an error message if the user doesn't exist.
    """

    database = "istreet"
    if not request.args.has_key("fb_id"):
        query = "SELECT * FROM user WHERE netid = %s"
        params = (netid, )
        userCursor = sendQuery(query, database, params = params)
    else:
        fb_id = request.args.get("fb_id")
        query = "SELECT * FROM user WHERE fb_id = %s"
        params = (fb_id, )
        userCursor = sendQuery(query, database, params = params)
    
    theUser = userCursor.fetchone()
    
    if theUser == None:
        return "Error: user does not exist"
    
    userEvents = theUser["events"]
    
    if userEvents == None or userEvents == "":
        eventsArray = []
    else:
        eventsArray = userEvents.split(", ")
        
    for i in range(len(eventsArray)):
        eventsArray[i] = {"event_id" : eventsArray[i]}
    
    return str(json.dumps(eventsArray, encoding = "latin-1"))
    
    

@app.route('/checkUser', methods = ['GET'])
@requires_CASauth
@requires_CRauth
def checkUser(netid):
    """
    Check if the user defined by fb_id exists.
    
    Parameters:
    fb_id: HTTP GET (mandatory) (ex. fb_id=88888888)
    
    Returns "Yes" or "No", or an error message if the fb_id parameter is missing.
    """
    if not request.args.has_key("fb_id"):
        return "ERROR: missing fb_id parameter (HTTP GET)"
    
    fb_id = request.args.get("fb_id")
    query = "SELECT * FROM user WHERE fb_id = %s"
    database = "istreet"
    params = (fb_id, )
    userCursor = sendQuery(query, database, params = params)
    theUser = userCursor.fetchone()
    
    if theUser == None:
        return "No"
    else:
        return "Yes"

@app.route('/getUsers', methods = ['GET'])
@requires_CASauth
@requires_CRauth
def getUsers(netid):
    """
    Return a list of all fb_id's in the database.
    
    Parameters:
    (None)
    
    Returns a comma-separated list of fb_id users using the app.
    """
    
    query = "SELECT fb_id FROM user WHERE (fb_id IS NOT NULL AND fb_id != %s)"
    database = "istreet"
    params = ("", )
    cursor = sendQuery(query, database, params = params)
    
    row = cursor.fetchone()
    fb_ids = []
    while row:
        fb_ids.append(row["fb_id"])
        row = cursor.fetchone()
    
    return ", ".join(fb_ids)
