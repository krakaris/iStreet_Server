from flask import Flask
app = Flask(__name__)

import CASClient, chat, main, database, authentication, users

import datetime
#used for sessions
app.secret_key = "J\"JOx[Lq\'.jt7P.qT5i\'"
app.permanent_session_lifetime = datetime.timedelta(7)
app.session_cookie_name = "ISTREET_SESSION"
app.session_cookie_domain = "istreetsvr.heroku.com"