# coding: utf-8
import os
import time

os.environ['TZ'] = 'America/Chicago'
time.tzset()

from flask import Flask

# Setup application
app = Flask(__name__)

# index.SETTINGS tells us which settings file to load for this env
from wsgi import SETTINGS
settings = __import__('laststatement.settings.%s' % SETTINGS,
                      fromlist=['DEBUG', 'SECRET', 'SQLURI'])

app.debug = settings.DEBUG
app.config['SECRET_KEY'] = settings.SECRET
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLURI

try:
    TWITTER_CONSUMER_KEY = settings.TWITTER_CONSUMER_KEY
    TWITTER_CONSUMER_SECRET = settings.TWITTER_CONSUMER_SECRET
    TWITTER_ACCESS_TOKEN = settings.TWITTER_ACCESS_TOKEN
    TWITTER_ACCESS_TOKEN_SECRET = settings.TWITTER_ACCESS_TOKEN_SECRET

    SMTP_FROM = settings.SMTP_FROM
    SMTP_USER = settings.SMTP_USER
    SMTP_PASS = settings.SMTP_PASS
    SMTP_HOST = settings.SMTP_HOST

    NOTIFY_EMAIL = settings.NOTIFY_EMAIL
except KeyError:
    pass

from admin.views import admin
from api.views import api

app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(api, url_prefix='/api/1')

import views

if __name__ == "__main__":
    app.run(debug=True)
