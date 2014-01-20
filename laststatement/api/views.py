# coding: utf-8

from datetime import datetime
from calendar import month_abbr

from passlib.hash import bcrypt

from flask import (Blueprint, current_app, request, json, jsonify)
from flask.ext.login import login_required
from sqlalchemy.sql import func

from laststatement.models import db, Offender, Term, Sentiment
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
    """ Create admin user """

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
@api.route('/executions', methods=['GET', 'OPTIONS'])
def executions_service(id=None):
    """ Query executions by ID or execution data.
    """

    if request.method == 'GET':
        races = {'b': 'Black', 'h': 'Hispanic', 'w': 'White', 'o': 'Other'}

        name = request.args.get('name', None)
        race = request.args.get('race', None)
        since = request.args.get('since', None)
        until = request.args.get('until', None)
        age_gt = request.args.get('age_gt', None)
        age_lt = request.args.get('age_lt', None)
        has_statement = request.args.get('has_statement', 't')
        # inc_statement = request.args.get('inc_statement', 't')

        q = db.session.query(Offender)
        err = []

        if id is None or id == 'all':
            if name is not None:
                last_name = name.split(',')[0]
                q = q.filter(Offender.last_name.ilike(last_name + '%'))

                try:
                    q = q.filter(Offender.first_name.ilike(name.split(',')[1]))
                except IndexError:
                    pass

            if race is not None:
                try:
                    race_list = [races[r] for r in race.split(',')]
                    q = q.filter(Offender.race.in_(race_list))
                except KeyError:
                    err.append('race parameter malformed; ignoring')

            if age_gt is not None:
                if age_gt.isdigit():
                    q = q.filter(Offender.age > age_gt)

            if age_lt is not None:
                if age_lt.isdigit():
                    q = q.filter(Offender.age < age_lt)

            if since is not None:
                try:
                    since = datetime.strptime(since, '%Y-%m-%d')
                    q = q.filter(Offender.execution_date >= since)
                except ValueError:
                    err.append('since parameter malformed; ignoring')

            if until is not None:
                try:
                    since = datetime.strptime(until, '%Y-%m-%d')
                    q = q.filter(Offender.execution_date <= until)
                except ValueError:
                    err.append('until parameter malformed; ignoring')

            if has_statement == 't':
                q = q.filter(Offender.last_statement != None)

        else:
            q = q.filter(Offender.execution_num == id)

        count = q.count()
        q = q.order_by(Offender.execution_num).all()

        corpus = [{'id': o.execution_num,
                   'first_name': o.first_name,
                   'last_name': o.last_name,
                   'race': o.race,
                   'age': o.age,
                   'execution_date': o.execution_date.strftime('%Y-%m-%d'),
                   'execution_num': o.execution_num,
                   'statement': o.last_statement,
                   'teaser': o.teaser,
                   'info_url': o.info_url,
                   'sentiments': [s.id for s in o.sentiments]}
                  for o in q]

        return jsonify(count=count, errors=err, executions=corpus)


@api.route('/executions/<id>', methods=['PUT', 'OPTIONS'])
@login_required
def executions_edit(id=None):
    """ Allows editing of offender records
        At this point, this is limited to adding / updating a teaser
    """
    if request.method == 'PUT':
        data = json.loads(request.data)

        o = db.session.query(Offender).\
            filter(Offender.execution_num == int(id)).first()

        try:
            o.teaser = data['teaser']
        except KeyError:
            pass

        try:
            sentiment_id = int(data['sentiments'])
            add = data['add']
        except KeyError:
            pass
        else:
            sentiment = db.session.query(Sentiment).get(sentiment_id)

            if add is True:
                o.sentiments.append(sentiment)
                current_app.logger.debug(o.sentiments)
            elif add is False:
                o.sentiments.remove(sentiment)
                current_app.logger.debug(o.sentiments)

        db.session.commit()

        sentiments = [s.id for s in o.sentiments]

        return jsonify(first_name=o.first_name, last_name=o.last_name,
                       race=o.race, age=o.age, execution_num=o.execution_num,
                       execution_date=o.execution_date.strftime('%Y-%m-%d'),
                       statement=o.last_statement, id=o.execution_num,
                       teaser=o.teaser, sentiments=sentiments)


@api.route('/terms/<id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
@api.route('/terms', methods=['POST', 'OPTIONS'])
@login_required
def terms_service(id=None):
    """ Used for editable table in admin.
        GET: return record(s) for existing terms
        PUT: update fields on existing terms
    """
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

    elif request.method == 'DELETE':
        if id.isdigit():
            try:
                term = db.session.query(Term).get(int(id))
                del_id = term.id
                db.session.delete(term)
                db.session.commit()
            except:
                return jsonify(success='false')
            else:
                return jsonify(id=del_id, success='true')

    elif request.method == 'POST':
        data = json.loads(request.data)
        term = Term(data['title'], [data['words']], data['chart'])

        db.session.add(term)
        db.session.commit()

        term_obj = {
            'id': term.id,
            'title': term.title,
            'words': term.words,
            'chart': term.chart
        }

        return jsonify(term=term_obj, success='true')

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

        return jsonify(id=term.id, title=term.title, chart=term.chart,
                       words=', '.join(term.words))
    else:
        return jsonify(success='false')


@api.route('/terms/data/', methods=['GET', 'OPTIONS'])
def terms_data_all():
    """ Looks up data for all existing terms.
        Returns list of terms containing title and raw count of statements
        containing term.
    """
    terms = db.session.query(Term).filter(Term.chart == True).all()
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
    """ Looks up data for a given term.
        Should return:
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


@api.route('/sentiments/<id>', methods=['GET', 'OPTIONS'])
def sentiments_service_public(id=None):
    """ Public sentiments endpoint.
        GET: return record(s) for existing sentiments
    """

    if request.method == 'GET':
        if id == 'all':
            statement_count = Offender.query.\
                filter(Offender.last_statement != None).count()

            sentiments = Sentiment.query.order_by('title').all()
            stmt_list = [
                {'id': s.id,
                 'title': s.title,
                 'execution_count': len(s.offenders),
                 'executions': [o.execution_num for o in s.offenders],
                 'active': s.active
                 } for s in sentiments]

            return jsonify(sentiments=stmt_list,
                           statement_count=statement_count)
        elif id.isdigit():
            sentiment = Sentiment.query.filter(Sentiment.id == int(id)).first()
            stmt_obj = {
                'id': sentiment.id,
                'title': sentiment.title
            }

            return jsonify(sentiment=stmt_obj)
        else:
            return jsonify(success='false')


@api.route('/sentiments/<id>', methods=['PUT', 'DELETE', 'OPTIONS'])
@api.route('/sentiments', methods=['POST', 'OPTIONS'])
@login_required
def sentiments_service(id=None):
    """ Used for editable table in admin.
        Implements DELETE, POST, and PUT methods
    """

    if request.method == 'DELETE':
        if id.isdigit():
            try:
                sntmt = db.session.query(Sentiment).get(int(id))
                del_id = sntmt.id
                db.session.delete(sntmt)
                db.session.commit()
            except:
                return jsonify(success='false')
            else:
                return jsonify(id=del_id, success='true')

    elif request.method == 'POST':
        data = json.loads(request.data)
        sntmt = Sentiment(data['title'])

        try:
            db.session.add(sntmt)
            db.session.commit()

            sntmt_obj = {
                'id': sntmt.id,
                'title': sntmt.title,
            }
        except:
            return jsonify(success='false')

        return jsonify(sentiment=sntmt_obj, success='true')

    elif request.method == 'PUT':
        data = json.loads(request.data)

        sentiment = db.session.query(Sentiment).get(int(id))

        try:
            sentiment.title = data['title']
        except KeyError:
            pass

        try:
            if data['active'] == 'true':
                sentiment.active = True
            elif data['active'] == 'false':
                sentiment.active = False
        except KeyError:
            pass

        db.session.commit()

        return jsonify(id=sentiment.id, title=sentiment.title)
    else:
        return jsonify(success='false')
