
import os
from MySQLdb import connect
from MySQLdb import cursors

import json
import chat

from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def index():
    return 'Uses: /eventslist, /eventinfo, /clubevents'

@app.route('/eventslist', methods = ['GET'])
def eventsList():
    #return getJSONForQuery("select title, event_id, poster, name, DATE(time_start) from pam_event, pam_club WHERE pam_club.club_id = pam_event.club_id AND DATE(time_start) = '2012-04-07'", "tigerapps")
    return getJSONForQuery("select title, event_id, poster, name, DATE(time_start) from pam_event, pam_club WHERE pam_club.club_id = pam_event.club_id AND DATE(time_start) <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) and time_start >= CURDATE() ORDER BY time_start", "tigerapps")

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

    return getJSONForQuery("select title, event_id, poster, time_start, time_end, description, entry, entry_description, name from pam_event, pam_club where pam_event.club_id = pam_club.club_id and time_start <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) and time_start >= CURDATE() and name = \"" + name + "\" ORDER BY time_start", "tigerapps")

def getJSONForQuery(query, database):
    cursor = sendQuery(query, database)
    table = getDictForQueryResults(cursor)
    return str(json.dumps(table, encoding = "latin-1"))

def sendQuery(query, database):
    host = 'www.tigerapps.org'
    user = 'iossvr24093'
    passwd = 'FpmMQe9MQRXgO63'
    
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

@app.route("/test")
def test():
    return add_message.test()

@app.route('/add', methods = ['POST'])
def add_message():
    user_id = request.form['user_id']
    message = request.form['message']
    print user_id
    print message
    print "hippo"
    return add_message.add(user_id, message)

@app.route('/get', methods = ['GET'])
def get_messages():
    past = request.args.get("past")
    if past == None:
        past = ""

    return get_messages(past)

if __name__ == '__main__':
    #app.debug = True
    #app.run()
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
