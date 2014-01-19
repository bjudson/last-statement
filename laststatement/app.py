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

from admin.views import admin
from api.views import api

app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(api, url_prefix='/api/1')

import views

if __name__ == "__main__":
    app.run(debug=True)
