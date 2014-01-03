# coding: utf-8

from datetime import datetime

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin

from laststatement.app import app

db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(60))
    active = db.Column(db.Boolean)
    created = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)

    def __init__(self, email, password, active=True):
        self.email = email
        self.password = password
        self.active = active
        self.created = datetime.now()

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def __repr__(self):
        return "<User %s>" % self.email
