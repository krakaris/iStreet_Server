from istreetserver import app

import sys

from flask import request, render_template, redirect, session
from authentication import authenticate
from database import getJSONForQuery, sendQuery

@app.route('/')
def index():
    netid = ""
    if 'username' in session:
        netid = session['username']
    return render_template('test.html', netid=netid)

@app.route('/eventslist', methods = ['GET'])
def eventsList():
    response = authenticate()
    if(type(response) != str):
        return response #redirect

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
    response = authenticate()
    if(type(response) != str):
        return response #redirect
   
    name = request.args.get("name")
    if name == None:
        return "Invalid request: missing name argument"
    
    return getJSONForQuery("select title, event_id, poster, time_start, time_end, description, entry, entry_description, name from pam_event, pam_club where pam_event.club_id = pam_club.club_id and DATE(time_start) > '2012-03-30' and name = \"" + name + "\" ORDER BY time_start", "tigerapps")

    #return getJSONForQuery("select title, event_id, poster, time_start, time_end, description, entry, entry_description, name from pam_event, pam_club where pam_event.club_id = pam_club.club_id and time_start <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) and time_start >= CURDATE() and name = \"" + name + "\" ORDER BY time_start", "tigerapps")

@app.route('/clubslist', methods = ['GET'])
def clubsList():
    response = authenticate()
    if(type(response) != str):
        return response #redirect
        
    return getJSONForQuery("select club_id, name from pam_club", "tigerapps")


