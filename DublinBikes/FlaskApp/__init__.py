from flask import Flask

app = Flask(__name__)

app.secret_key = '12345'

# Import routes to register them with the app.
from DublinBikes.FlaskApp import routes
