# coding: utf-8

import re
from datetime import datetime

from flask import (abort, render_template, Markup)

from app import app
from models import db, Offender
from helpers import date2text, doy_leap


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
                html += (u'<a id="data-btn" class="icon-btn" href='
                         u'"/sentiments" title="View sentiment data">'
                         u'</a>')
            if b == 'twitter':
                html += (u'<a id="twitter-btn" class="icon-btn" href='
                         u'"http://twitter.com/LastStatementTx" title='
                         u'"Twitter bot"></a>')
            if b == 'api':
                html += (u'<a id="api-btn" class="icon-btn" href="/api"'
                         u' title="Use API"></a>')
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
                                Offender.gender,
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
                                    Offender.gender,
                                    Offender.execution_date,
                                    Offender.info_url,
                                    Offender.execution_num,
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


###############################################################################
#
#   Angular app routes
#
###############################################################################


@app.route('/sentiments/', methods=['GET', 'OPTIONS'])
def sentiments():
    js = [
        'sentiments/ng-app/app.js',
        'sentiments/ng-app/services.js',
        'sentiments/ng-app/controllers.js',
        'sentiments/ng-app/directives.js'
    ]

    css = [
        'last.css?v=7',
        'sentiments/css/sentiments.css?v=1'
    ]

    return render_template('apps/index.html', app_name='sentimentApp',
                           page_title='Last Statement Sentiments',
                           js=js, css=css)


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
