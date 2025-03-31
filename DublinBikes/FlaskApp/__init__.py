from flask import Flask

app = Flask(__name__)

app.secret_key = "12345"

# Import routes to register them with the app.
from DublinBikes.FlaskApp import routes


# This is a context processor that will inject the timedelta function into all templates.
# This will allow us to do things like {{ now + timedelta(days=3) }} in templates.
# --> Useage: in the Hoome template to select a date
from datetime import timedelta


@app.context_processor
def inject_timedelta():
    return dict(timedelta=timedelta)
