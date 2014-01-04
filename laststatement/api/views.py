# coding: utf-8

from calendar import month_abbr

from passlib.hash import bcrypt

from flask import (Blueprint, request, json, jsonify)
from flask.ext.login import login_required
from sqlalchemy.sql import func

from laststatement.models import db, Offender, Term
from laststatement.admin.models import User
from laststatement.helpers import date2text

api = Blueprint('api', __name__)


#
# Data retreival / calculation functions
#


def get_span_totals(type):
    """ Returns dict with key = time span label, val = # of statements"""
    if(type in ['month', 'year']):
        col = getattr(Offender, 'execution_%s' % type)

        span_counts = db.session.query(col, func.count(col)).\
            filter(Offender.last_statement != None).\
            group_by(col).all()

        return {str(int(s[0])): s[1] for s in span_counts}
    else:
        return {}


def get_colocations(term):
    """ Takes a single term, returns number of times all other terms occur in
        statements with it
    """
    terms = db.session.query(Term).filter(Term.title != term.title,
                                          Term.chart == True)
    term_list = []
    for t in terms:
        viewing = ' | '.join(term.words)
        against = ' | '.join(t.words)
        count = db.session.query(Offender).\
            filter('to_tsvector(offenders.last_statement) '
                   '@@ to_tsquery(\'(%s) & (%s)\')' % (viewing, against)).\
            count()
        term_list.append({'term': t.title, 'count': count})

    return sorted(term_list, key=lambda t: t['count'])


def statement_time_calc(offenders, type):
    """ Takes offenders, returns list of dicts with time span label,
        percent of statements, count of statements
    """
    if(type in ['month', 'year']):
        span_perc = []
        span_dict = {}
        span_totals = get_span_totals(type)

        for o in offenders:
            period = str(getattr(o.execution_date, type))
            try:
                span_dict[period] += 1
            except KeyError:
                span_dict[period] = 1

        for s, c in span_totals.items():
            stmt_count = span_dict.get(s, 0)
            percent = round(float(stmt_count) / float(c) * 100, 1)
            span_perc.append({type: s, 'percent': percent,
                              'count': stmt_count})

        return span_perc
    else:
        return []

###############################################################################
#
#   Routes
#
###############################################################################


@api.route('/', methods=['GET', 'OPTIONS'])
def index():
    return jsonify(success='true')


@api.route('/user', methods=['GET', 'POST', 'OPTIONS'])
@login_required
def user_add():
    if request.method == 'POST':
        email = request.form.get('email')
        existing = db.session.query(User).filter(User.email == email).first()

        if existing is None:
            password = bcrypt.encrypt(request.form.get('password'), rounds=12)

            # try:
            u = User(email=email, password=password)

            db.session.add(u)
            db.session.commit()

            return jsonify(email=email, success='true')
        else:
            return jsonify(error='Email already exists', success='false')


@api.route('/executions/<id>', methods=['GET', 'OPTIONS'])
def executions_service(id=None):
    """ Query executions.
        TODO - parameters:
        * Date (day, range)
        * Terms (freeform?)
        * Race
        * Gender
        * Name
    """

    offenders = db.session.query(Offender).\
        filter(Offender.last_statement != None).\
        order_by(Offender.execution_num).\
        all()

    corpus = [{'first_name': o.first_name,
               'last_name': o.last_name,
               'execution_date': o.execution_date.strftime('%Y-%m-%d'),
               'execution_num': o.execution_num,
               'statement': o.last_statement}
              for o in offenders]

    return jsonify(offenders=corpus)


@api.route('/terms/<id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
@login_required
def terms_service(id=None):
    if request.method == 'GET':
        if id == 'all':
            terms = Term.query.order_by('title').all()
            term_list = [
                {'id': t.id,
                 'title': t.title,
                 'words': ', '.join(t.words),
                 'chart': t.chart
                 } for t in terms]

            return jsonify(terms=term_list)
        elif id.isdigit():
            term = Term.query.filter(Term.id == int(id)).first()
            term_obj = {
                'id': term.id,
                'title': term.title,
                'words': ', '.join(term.words),
                'chart': term.chart
            }

            return jsonify(term=term_obj)
        else:
            return jsonify(success='false')

    elif request.method == 'POST':
        # TODO: Implement POST
        return jsonify(error='Method not implemented', success='false')

    elif request.method == 'PUT':
        data = json.loads(request.data)

        term = db.session.query(Term).get(int(id))

        try:
            term.title = data['title']
        except KeyError:
            pass

        try:
            if data['chart'] == 'true':
                term.chart = True
            elif data['chart'] == 'false':
                term.chart = False
        except KeyError:
            pass

        try:
            term.words = [w.strip() for w in data['words'].split(',')]
        except KeyError:
            pass

        db.session.commit()

        term_obj = {
            'id': term.id,
            'title': term.title,
            'chart': term.chart,
            'words': term.words,
        }

        return jsonify(id=term.id, title=term.title, chart=term.chart,
                       words=', '.join(term.words))
    else:
        return jsonify(success='false')


@api.route('/terms/data/', methods=['GET', 'OPTIONS'])
def terms_data_all():
    terms = db.session.query(Term).filter(Term.chart).all()
    term_list = []

    for t in terms:
        count = db.session.query(Offender).\
            filter('to_tsvector(offenders.last_statement) '
                   '@@ to_tsquery(\'%s\')' % ' | '.join(t.words)).count()
        term_list.append({'term': t.title, 'count': str(count)})

    term_list = sorted(term_list, key=lambda t: t['count'])

    return jsonify(success='true', terms=term_list)


@api.route('/terms/data/<term>', methods=['GET', 'OPTIONS'])
def terms_data_single(term):
    """ Looks up data for a given term. Should return:
        * Term record (title, words used in search)
        * All other terms, sorted by # of times they appear with given term
        * All years with percent of statements containing given term
        * All statements containing this term
    """
    term_view = db.session.query(Term).filter(Term.title == term).first()

    if(term_view is not None):
        colocations = get_colocations(term_view)

        offenders = db.session.query(Offender).\
            filter('to_tsvector(offenders.last_statement) '
                   '@@ to_tsquery(\'%s\')' % ' | '.join(term_view.words)).\
            order_by(Offender.execution_date).all()

        year_perc = statement_time_calc(offenders, 'year')
        month_perc = statement_time_calc(offenders, 'month')

        years = sorted(year_perc, key=lambda r: r['year'])

        months = []
        for i in xrange(1, 13):
            d = (item for item in month_perc if item['month'] == str(i)).next()
            d['month'] = month_abbr[i]
            months.append(d)

        statements = []
        for o in offenders:
            statements.append({'statement': o.last_statement,
                               'name': '%s %s' % (o.first_name, o.last_name),
                               'date': date2text(o.execution_date),
                               'month': o.execution_date.month,
                               'year': o.execution_date.year})

        term_view = {'title': term_view.title, 'words': term_view.words}

        return jsonify(success='true', viewing=term_view, terms=colocations,
                       years=years, months=months, statements=statements)
    else:
        return jsonify(success='false')
