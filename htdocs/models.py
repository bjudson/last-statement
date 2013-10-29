# coding: utf-8

from datetime import datetime

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql
from flask.ext.login import UserMixin

from last import app
import views

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


class Offender(db.Model):
    __tablename__ = 'offenders'
    id = db.Column(db.Integer, primary_key=True)
    tdcj_id = db.Column(db.Integer)
    last_name = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    dob = db.Column(db.Date)
    execution_num = db.Column(db.Integer)
    execution_date = db.Column(db.Date)
    execution_day = db.Column(db.Integer)
    offense_date = db.Column(db.Date)
    offense_county = db.Column(db.String(50))
    received_date = db.Column(db.Date)
    gender = db.Column(db.String(1))
    race = db.Column(db.String(20))
    last_statement = db.Column(db.Text)
    info_url = db.Column(db.String(200))
    statement_url = db.Column(db.String(200))

    def __init__(self, id=None, tdcj_id=None, last_name=None, first_name=None,
                 age=None, dob=None, execution_num=None, execution_date=None,
                 offense_date=None, offense_county=None,
                 received_date=None, gender=None, race=None,
                 last_statement=None, info_url=None, statement_url=None):
        self.tdcj_id = tdcj_id
        self.last_name = last_name
        self.first_name = first_name
        self.age = age
        self.dob = dob
        self.execution_num = execution_num
        self.execution_date = execution_date
        self.execution_day = views.doy_leap(execution_date)
        self.offense_date = offense_date
        self.offense_county = offense_county
        self.received_date = received_date
        self.gender = gender
        self.race = race
        self.last_statement = last_statement
        self.info_url = info_url
        self.statement_url = statement_url


class Term(db.Model):
    __tablename__ = 'terms'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    words = db.Column(postgresql.ARRAY(db.String(50)))
    chart = db.Column(db.Boolean)

    def __init__(self, title=None, words=None):
        self.title = title
        self.words = words
