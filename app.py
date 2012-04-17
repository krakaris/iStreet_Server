
import os
from MySQLdb import connect
from MySQLdb import cursors

import json, chat, string, sys

from flask import Flask, request, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('test.html')
    #return 'Uses: /eventslist, /eventinfo, /clubevents'

@app.route('/eventslist', methods = ['GET'])
def eventsList():
    return getJSONForQuery("select title, event_id, poster, name, time_start from pam_event, pam_club WHERE pam_club.club_id = pam_event.club_id AND DATE(time_start) > '2012-03-30'", "tigerapps")
#    return getJSONForQuery("select title, event_id, poster, name, time_start from pam_event, pam_club WHERE pam_club.club_id = pam_event.club_id AND DATE(time_start) <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) and time_start >= CURDATE() ORDER BY time_start", "tigerapps")

@app.route('/eventinfo', methods = ['GET'])
def eventInfo():
    event_id = request.args.get("event_id")
    if event_id == None:
        return "Invalid request: missing event_id argument"

    return getJSONForQuery("select title, poster, event_id, time_start, time_end, description, entry, entry_description, name from pam_event, pam_club where pam_event.club_id = pam_club.club_id and event_id = " + str(event_id), "tigerapps")

@app.route('/clubevents', methods = ['GET'])
def clubEvents():
    name = request.args.get("name")
    if name == None:
        return "Invalid request: missing name argument"
    
    return getJSONForQuery("select title, event_id, poster, time_start, time_end, description, entry, entry_description, name from pam_event, pam_club where pam_event.club_id = pam_club.club_id and time_start >= '2012-03-07' and name = \"" + name + "\" ORDER BY time_start", "tigerapps")

    #return getJSONForQuery("select title, event_id, poster, time_start, time_end, description, entry, entry_description, name from pam_event, pam_club where pam_event.club_id = pam_club.club_id and time_start <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) and time_start >= CURDATE() and name = \"" + name + "\" ORDER BY time_start", "tigerapps")

@app.route('/clubslist', methods = ['GET'])
def clubsList():
    return getJSONForQuery("select club_id, name from pam_club", "tigerapps")

def getJSONForQuery(query, database):
    cursor = sendQuery(query, database)
    table = getDictForQueryResults(cursor)
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

def getDictForQueryResults(cursor):
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

    #TODO: what if the following two args dont exist?
    user_id = request.form['user_id']
    message = request.form['message']
    print user_id
    print message
    return chat.add(user_id, message)

@app.route('/get', methods = ['GET'])
def get_messages():
    past = request.args.get("past")
    if past == None:
        past = ""
    return chat.get(past)

if __name__ == '__main__':
    if(len(sys.argv) > 1 and str.lower(sys.argv[1]) == "debug"):
        app.debug = True
        app.run()
    else:
        # Bind to PORT if defined, otherwise default to 5000.
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
