from istreetserver import app

import sys

from flask import request, render_template, redirect, session
from authentication import authenticate
from database import sendQuery

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
    query = str.format("SELECT fb_id FROM user WHERE events REGEXP \'^{0}, \' or events REGEXP \', {0}, \' or events REGEXP \', {0}$\'", event_id)
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
