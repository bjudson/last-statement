# coding: utf-8

import os
import re
import time
from datetime import datetime

from flask import (abort, render_template, Markup)

from app import app
from admin.views import admin
from api.views import api
from models import db, Offender
from helpers import date2text

os.environ['TZ'] = 'America/Chicago'
time.tzset()

app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(api, url_prefix='/api/1')

#
# Helper functions
#


def doy_leap(date=None):
    """ Adjust day of year int to account for leap year.

        Not an ideal solution, but we are simply subtracting 1 from tm_yday if
        tm_year is found to be leap and tm_yday > 60 (Feb 29). Thus, Feb 29 is
        indistinguishable from March 1, but every year has 365 days.
    """

    doy = date.timetuple().tm_yday
    year = date.timetuple().tm_year

    if year % 4 == 0:
        if doy > 60:
            doy -= 1

    return doy


###############################################################################
#
#   Context processors
#
###############################################################################

@app.context_processor
def nav():
    """ Makes function for building nav element available in all templates """
    def top_nav(buttons=('home', 'info', 'github')):
        """ Returns HTML nav element with selected buttons """
        html = u'<nav class="menu">'
        for b in buttons:
            if b == 'home':
                html += (u'<a id="cal-btn" class="icon-btn" href="/" title="'
                         u'Today’s last statement">☼</a> ')
            if b == 'data':
                html += (u'<a id="data-btn" class="icon-btn" href="/terms" '
                         u'title="Go to last statement data">%</a>')
            if b == 'info':
                html += (u'<a id="info-btn" class="icon-btn" href="javascript:'
                         u'void(0)" title="About this page">i</a> ')
            if b == 'github':
                html += (u'<a id="github-btn" class="icon-btn" href="https://'
                         u'github.com/bjudson/last-statement" title="Get the '
                         u'code">#</a> ')
        html += u'</nav>'

        return Markup(html)
    return dict(top_nav=top_nav)


@app.context_processor
def exec_total():
    """ Makes total number of executions available in all templates """
    return dict(exec_total=db.session.query(Offender).count())


###############################################################################
#
#   Public routes
#
###############################################################################


@app.route("/", methods=['GET', 'OPTIONS'])
def index():
    """ Show statement for someone executed on this date, or nearest date """

    day_of_year = doy_leap(datetime.now())

    offender = db.session.query(Offender.first_name, Offender.last_name,
                                Offender.execution_date,
                                Offender.execution_num,
                                Offender.last_statement).\
        filter(Offender.last_statement != None).\
        order_by('abs(%i - offenders.execution_day)' % day_of_year).\
        first()

    if offender is None:
        abort(404)

    exec_date = date2text(offender.execution_date)

    return render_template('home.html', offender=offender,
                           exec_date=exec_date)


@app.route("/execution/<num>", methods=['GET', 'OPTIONS'])
def execution_num(num):
    """ Find last statement by execution number """

    if num.isdigit():
        offender = db.session.query(Offender.first_name, Offender.last_name,
                                    Offender.execution_date,
                                    Offender.last_statement).\
            filter(Offender.execution_num == num).\
            first()

        if offender is None:
            abort(404)
    else:
        abort(404)

    exec_date_text = offender.execution_date.strftime('%-d %B %Y')

    return render_template('number.html', offender=offender,
                           exec_date=exec_date_text)


@app.route("/all", methods=['GET', 'OPTIONS'])
def all():
    """ Show all statements """

    offenders = db.session.query(Offender.first_name, Offender.last_name,
                                 Offender.age,
                                 Offender.race,
                                 Offender.execution_date,
                                 Offender.execution_num,
                                 Offender.last_statement).\
        filter(Offender.last_statement != None).\
        order_by(Offender.execution_num).\
        all()

    return render_template('all.html', offenders=offenders)


@app.route('/all/text', methods=['GET', 'OPTIONS'])
def all_text():
    """ Save all statements to a single file, without names or HTML tags. """

    statements = db.session.query(Offender.last_statement).\
        filter(Offender.last_statement != None).\
        order_by(Offender.execution_num).\
        all()

    corpus = []
    for s in statements:
        corpus.append(s.last_statement)

    text = re.sub('<[^<]+?>', '', ' '.join(corpus))

    return render_template('text.html', body=text)


@app.route('/terms', methods=['GET', 'OPTIONS'])
def terms_index():
    """ The main terms page. Content is loaded by JS through API """
    return render_template('terms.html')


###############################################################################
#
#   Error handlers
#
###############################################################################


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
