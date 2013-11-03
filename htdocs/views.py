# coding: utf-8

import os
import urllib2
import shutil
import re
import time
from datetime import datetime
from calendar import month_abbr
from collections import OrderedDict
# from pprint import PrettyPrinter

from passlib.hash import bcrypt
from bs4 import BeautifulSoup

from flask import (request, abort, render_template, url_for, flash, redirect,
                   jsonify)
from sqlalchemy.orm import exc
from sqlalchemy.sql import func
from flask.ext.login import (LoginManager, login_user, logout_user,
                             current_user, login_required)

from last import app
from models import db, User, Offender, Term
from forms import LoginForm, UserAddForm

DEATH_ROW_URLS = {
    'base': 'http://www.tdcj.state.tx.us/death_row/',
    'executed': 'dr_executed_offenders.html',
    'received': 'dr_offenders_on_dr.html'
}

# JPG_INFO_PATH = '%s/%s' % (app.static_folder, 'info_img')
JPG_INFO_PATH = None

os.environ['TZ'] = 'America/Chicago'
time.tzset()

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

#
# Helper functions
#


@login_manager.user_loader
def load_user(userid):
    return db.session.query(User).get(userid)


def date2text(date=None):
    """ Convert date to human-friendly string
    """
    return date.strftime('%-d %B %Y')


def doy_leap(date=None):
    """ Adjust day of year int to account for leap year. Not an ideal solution,
        but we are simply subtracting 1 from tm_yday if tm_year is found to be
        leap and tm_yday > 60 (Feb 29). Thus, Feb 29 is indistinguishable from
        March 1, but every year has 365 days.
    """

    doy = date.timetuple().tm_yday
    year = date.timetuple().tm_year

    if year % 4 == 0:
        if doy > 60:
            doy -= 1

    return doy

#
# Data retreival / calculation functions
#


def get_span_totals(type):
    """ Returns dict with key = span label, val = # of statements"""
    if(type in ['month', 'year']):
        col = getattr(Offender, 'execution_%s' % type)

    span_counts = db.session.query(col, func.count(col)).\
        filter(Offender.last_statement != None).\
        group_by(col).all()

    return {str(int(s[0])): s[1] for s in span_counts}


def get_colocations(term):
    """ Takes a single term, returns number of times all other terms occur in
        statements with it
    """
    terms = db.session.query(Term).filter(Term.title != term.title, Term.chart)
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
#   Public routes
#
###############################################################################


@app.route("/", methods=['GET', 'OPTIONS'])
def index():
    """ Show the last statement for someone executed on this date, or date
        nearest available date.
    """

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

    exec_total = db.session.query(Offender).count()
    exec_date = date2text(offender.execution_date)

    return render_template('home.html', offender=offender,
                           exec_date=exec_date, exec_total=exec_total)


@app.route("/execution/<num>", methods=['GET', 'OPTIONS'])
def execution_num(num):
    """ Find last statement by execution number
    """

    offender = db.session.query(Offender.first_name, Offender.last_name,
                                Offender.execution_date,
                                Offender.last_statement).\
        filter(Offender.execution_num == num).\
        first()

    if offender is None:
        abort(404)

    exec_date_text = offender.execution_date.strftime('%-d %B %Y')

    return render_template('number.html', offender=offender,
                           exec_date=exec_date_text)


@app.route("/all", methods=['GET', 'OPTIONS'])
def all():
    """ Show all statements
    """

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
def save_text():
    """ Save all statements to a single file, without names or HTML tags.
    """

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
    """ The main terms page. Content is loaded by JS through data functions
        below.
    """
    return render_template('terms.html')


@app.route('/terms/data/', methods=['GET', 'OPTIONS'])
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


@app.route('/terms/data/<term>', methods=['GET', 'OPTIONS'])
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
                               'date': date2text(o.execution_date)})

        term_view = {'title': term_view.title, 'words': term_view.words}

        return jsonify(success='true', viewing=term_view, terms=colocations,
                       years=years, months=months, statements=statements)
    else:
        return jsonify(success='false')


###############################################################################
#
#   Admin routes
#
###############################################################################


@app.route('/login', methods=['GET', 'POST', 'OPTIONS'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and bcrypt.verify(form.password.data,
                                              user.password):
            if login_user(user):
                user.last_login = datetime.now()
                db.session.commit()

                flash('Logged in %s' % user.email, 'success')
                return redirect(request.args.get('next') or
                                url_for('dashboard'))
            else:
                flash('This user is disabled', 'error')
        else:
            flash('Wrong email or password', 'error')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out', 'success')
    return redirect(url_for('index'))


@app.route('/admin', methods=['GET', 'OPTIONS'])
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user.email)


@app.route('/admin/users/add', methods=['GET', 'POST', 'OPTIONS'])
@login_required
def user_add():
    form = UserAddForm()

    if request.method == 'POST':
        email = request.form.get('email')
        existing = db.session.query(User).filter(User.email == email).first()

        if existing is None:
            password = bcrypt.encrypt(request.form.get('password'), rounds=12)

            # try:
            u = User(email=email, password=password)

            db.session.add(u)
            db.session.commit()

            return redirect(url_for('dashboard'))
            # except:
            #     flash("Unable to save user.")
        else:
            flash("Email already exists.")

        return render_template('user_add.html', form=form)
    else:
        return render_template('user_add.html', form=form)


@app.route('/admin/scrape', methods=['GET', 'OPTIONS'])
@login_required
def scrape():
    """ Scrape data from TDCJ and save any new records found
        TODO: Scrape extra offender data. Much of this is in jpg files, so we
              will not be able to get a complete data set.
    """

    #
    # Scrape basic info for all executed offenders
    #

    # Map TDCJ table column headers to database fields
    exec_table_map = OrderedDict([
        ('execution_num', 'Execution'),
        ('info_url', 'Link'),
        ('statement_url', 'Link'),
        ('last_name', 'Last Name'),
        ('first_name', 'First Name'),
        ('tdcj_id', 'TDCJ Number'),
        ('age', 'Age'),
        ('execution_date', 'Date'),
        ('race', 'Race'),
        ('offense_county', 'County')
    ])

    doc = urllib2.urlopen(DEATH_ROW_URLS['base'] + DEATH_ROW_URLS['executed'])
    table = BeautifulSoup(doc).table

    # Sanity check: do headers match our map?
    headers = [f.string for f in table.find_all('th')]

    for header in exec_table_map.values():
        map_title = header
        table_title = headers.pop(0)

        if table_title != map_title:
            # Looks like format changed, log error & exit
            app.logger.debug(u'Table headers dont match map: %s (map) - %s '
                             '(table)' % (map_title, table_title))

    existing = db.session.query(Offender.tdcj_id).all()

    if len(existing) > 0:
        existing = map(list, zip(*existing))[0]

    data = []
    for r in table.find_all('tr'):
        row_data = {}
        cells = r.find_all('td')

        try:
            for column in exec_table_map.keys():
                cell = cells.pop(0)

                if cell.a is not None:
                    row_data[column] = cell.a['href']
                elif 'date' in column:
                    row_data[column] = datetime.strptime(cell.text, '%m/%d/%Y')
                else:
                    row_data[column] = cell.text

        except IndexError:
            # Just catches case where tr does not contain td (e.g. th only)
            pass

        else:
            data.append(row_data)

    already_imported = 0
    new_imports = 0

    for d in data:
        if int(d['tdcj_id']) in existing:
            already_imported += 1
        else:
            offndr = Offender(**d)
            db.session.add(offndr)
            new_imports += 1

    try:
        db.session.commit()
    except exc:
        app.logger.debug('Error saving records')

    #
    # Scrape last statements
    #

    missing_statement = db.session.query(Offender.id, Offender.statement_url).\
        filter(Offender.last_statement == None)

    statements_added = 0
    statements_failed = 0

    for r in missing_statement:
        off_id, state_url = r

        if state_url != 'dr_info/no_last_statement.html':
            state_doc = urllib2.urlopen(DEATH_ROW_URLS['base'] + state_url)
            soup = BeautifulSoup(state_doc)

            try:
                # The last statement documents have a paragraph containing
                # the text "Last Statement:" followed by various numbers of
                # spaces. The statement text is within one or more paragraphs
                # following this.
                statement_tags = soup.find(text=re.compile('Last Statement:'
                                                           '[\s-]*'))\
                    .parent.find_all_next('p')
            except AttributeError:
                statements_failed += 1
                app.logger.debug('Unable to get last statement for %s' %
                                 state_url)
            else:
                statements_added += 1
                statement_string = ' '.join([str(t) for t in statement_tags])
                db.session.query(Offender).filter(Offender.id == off_id).\
                    update({Offender.last_statement: statement_string})

    db.session.commit()

    #
    # Save jpg files
    #

    info_jpgs_downloaded = 0

    if JPG_INFO_PATH is not None and os.access(JPG_INFO_PATH, os.W_OK):
        with_jpg_info = db.session.query(Offender.id, Offender.execution_num,
                                         Offender.info_url).\
            filter(Offender.info_url.like("%.jpg%"))

        for o in with_jpg_info:
            jpg = urllib2.urlopen(DEATH_ROW_URLS['base'] + o.info_url)
            filename = '%i_%s' % (o.execution_num, o.info_url.split('/')[-1])
            with open('%s/%s' % (JPG_INFO_PATH, filename), 'wb') as fp:
                shutil.copyfileobj(jpg, fp)

            info_jpgs_downloaded += 1
    else:
        app.logger.debug('Unable to access JPG_INFO_PATH: %s' % JPG_INFO_PATH)

    return render_template('scrape_results.html', new_offenders=new_imports,
                           new_statements=statements_added,
                           statements_failed=statements_failed,
                           info_jpgs_downloaded=info_jpgs_downloaded)


###############################################################################
#
#   Error handlers
#
###############################################################################


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
