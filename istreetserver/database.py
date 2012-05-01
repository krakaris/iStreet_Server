import json

from MySQLdb import connect
from MySQLdb import cursors

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