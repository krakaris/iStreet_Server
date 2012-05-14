import sys, os

from istreetserver import app

if __name__ == '__main__':
    '''
    Run the server.
    '''
    if(len(sys.argv) > 1 and str.lower(sys.argv[1]) == "debug"):
        app.debug = True
        app.run()
    else:
        # Bind to PORT if defined, otherwise default to 5000.
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)