import json

from MySQLdb import connect, cursors

def getJSONForQuery(query, database, params = ()):
    '''
    Sends a MySQL query (a string) to the database (a string) on the USG server with the parameters (a tuple) given.
    Returns the results of the query in JSON form.
    '''
    cursor = sendQuery(query, database, params = params)
    table = getDictArrayForQueryResults(cursor)
    return str(json.dumps(table, encoding = "latin-1"))

def sendQuery(query, database, params = ()):
    '''
    Sends a MySQL query (a string) to the database (a string) on the USG server with the parameters (a tuple) given.
    Returns a cursor for the query.
    '''

    host = 'www.tigerapps.org'
    user = 'iossvr24093'
    passwd = 'FpmMQe9MQRXgO63'

    connection = connect(host = host, user = user, passwd = passwd, db = database)
    cursor = connection.cursor(cursors.DictCursor)
    cursor.execute(query, params)
    
    return cursor

def getDictArrayForQueryResults(cursor):
    '''
    Returns an array of dictionary for the results in the cursor.
    '''
    results = []
    row = cursor.fetchone()
    while row:
        for key in row:
            row[key] = str(row[key]) 
            '''necessary for things like datetime objects'''
        results.append(row)
        row = cursor.fetchone()
    return results
