# coding: utf-8
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

import views

if __name__ == "__main__":
    app.run(debug=True)
