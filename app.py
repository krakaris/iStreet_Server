import os

from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'Use: /name'

@app.route('/<name>')
def hello(name):
    return 'Hello, %s' % name

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
