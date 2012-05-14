from istreetserver import app

from flask import render_template, session, request
from authentication import requires_CASauth
from database import getJSONForQuery

@app.route('/')
def index():
    '''
    Returns HTML for the login page.
    '''
    netid = ""
    if 'username' in session:
        netid = session['username']
    return render_template('index.html', netid=netid)

@app.route('/eventslist', methods = ['GET'])
@requires_CASauth
def eventsList(netid):
    '''
    Returns JSON for the list of upcoming events (currently, for testing, we return events from the last month as well).
    '''
    query = "select title, event_id, poster, name, time_start, time_end, description, entry, entry_description from pam_event, pam_club WHERE pam_club.club_id = pam_event.club_id AND DATE(time_start) > '2012-04-10'";
    database = "tigerapps"
    return getJSONForQuery(query, database)


@app.route('/eventinfo', methods = ['GET'])
@requires_CASauth
def eventInfo(netid):
    '''
    Returns JSON information for the given event.
    
    Parameters:
    event_id: HTTP GET (required) (ex. event_id=105)
    '''
    event_id = request.args.get("event_id")
    if event_id == None:
        return "Invalid request: missing event_id argument"

    query = "select title, poster, event_id, time_start, time_end, description, entry, entry_description, name from pam_event, pam_club where pam_event.club_id = pam_club.club_id and event_id = %s"
    database = "tigerapps"
    params = (event_id, )
    return getJSONForQuery(query, database, params = params)

@app.route('/clubevents', methods = ['GET'])
@requires_CASauth
def clubEvents(netid):
    '''
    Returns JSON information for the events for the given club.
    
    Parameters:
    name: HTTP GET (required) (ex. name=Cannon)
    '''
    name = request.args.get("name")
    if name == None:
        return "Invalid request: missing name argument"
    
    query = "select title, event_id, poster, time_start, time_end, description, entry, entry_description, name from pam_event, pam_club where pam_event.club_id = pam_club.club_id and DATE(time_start) > '2012-04-10' and name = %s ORDER BY time_start"
    database = "tigerapps"
    params = (name, )
    return getJSONForQuery(query, database, params = params)

@app.route('/clubslist', methods = ['GET'])
@requires_CASauth
def clubsList(netid):
    '''
    Returns JSON information for the list of 11 clubs.
    '''
    return getJSONForQuery("select club_id, name from pam_club", "tigerapps")


