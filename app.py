import os
from MySQLdb import connect
from MySQLdb import cursors

from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'Use: /name'

@app.route('/<name>')
def hello(name):
    return 'param: %s' % name

@app.route('/eventslist')
def eventsList():
    host = 'www.tigerapps.org'
    port = 5001
    user = 'rnarang'
    passwd = 'temporaryaccess'
    db = 'tigerapps'
    connection = connect(host = host, port = port, user = user, passwd = passwd, db = db)

    # Create cursor as a dictionary:
    cursor = connection.cursor(cursors.DictCursor)
    cursor.execute("select * from pam_event")
    row = cursor.fetchone()
    table = ""
    while row:
        table = table + row[title] + ", "
        row = cursor.fetchone()

    return table

if __name__ == '__main__':
    #app.debug = True
    #app.run()
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
