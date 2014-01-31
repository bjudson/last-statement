# coding: utf-8

import os
import urllib2
import shutil
import re
import time
from datetime import datetime
from collections import OrderedDict

from bs4 import BeautifulSoup
import tweepy

from flask.ext.script import Manager
from sqlalchemy import not_
from sqlalchemy.orm import exc

from laststatement.wsgi import application as app
from laststatement.models import db, Offender, Term
from laststatement.app import TWITTER_CONSUMER_KEY,\
    TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN,\
    TWITTER_ACCESS_TOKEN_SECRET
from laststatement.helpers import doy_leap

DEATH_ROW_URLS = {
    'base': 'http://www.tdcj.state.tx.us/death_row/',
    'executed': 'dr_executed_offenders.html',
    'received': 'dr_offenders_on_dr.html'
}

JPG_INFO_PATH = '%s/%s' % (app.static_folder, 'info_img')
# JPG_INFO_PATH = None

os.environ['TZ'] = 'America/Chicago'
time.tzset()

date = datetime.now().strftime('%Y-%m-%d %H:%M')

manager = Manager(app)


@manager.command
def term_map():
    """ Search statements for terms and save relationships
        Finds term(s), performs full-text search of all statements, saves
        in join table.
    """

    terms = db.session.query(Term).all()
    term_joins = []

    for t in terms:
        offenders = db.session.query(Offender).\
            filter('to_tsvector(offenders.last_statement) '
                   '@@ to_tsquery(\'%s\')' % ' | '.join(t.words)).all()

        for o in offenders:
            term_joins.append({'term_id': t.id, 'offender_id': o.id})


@manager.command
def tweet():
    """ Look for statements made on this day, tweet teaser + link

        In practice, this is called using a cron job once a day. Cron needs
        to activate virtual environment before using this command.
    """

    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    twitter = tweepy.API(auth)

    # returns 20 most recent statuses
    recents = twitter.user_timeline()
    posted = [r.text.split(' http')[0] for r in recents]
    similar = "%|".join(posted) + "%"  # postgres SIMILAR TO syntax

    day_of_year = doy_leap(datetime.now())
    date = datetime.now().strftime('%Y-%m-%d %H:%M')

    offender = db.session.query(Offender.execution_num,
                                Offender.teaser,
                                not_(Offender.teaser.op("SIMILAR TO")(similar))).\
        filter(Offender.teaser != None).\
        filter(Offender.execution_day == day_of_year).first()

    if offender is not None:
        try:
            url = "http://laststatement.org/execution/%s" % \
                offender.execution_num
            twitter.update_status("%s %s" % (offender.teaser, url))
        except tweepy.TweepError as e:
            print "%s Error: %s (%s)" % (date,
                                         e.message[0]['message'],
                                         e.message[0]['code'])
    else:
        print '%s Notice: No statement for today' % date


def get_existing_offenders():
    """ Get TDCJ IDs of all executed offenders in database"""

    existing = db.session.query(Offender.tdcj_id).all()

    if len(existing) > 0:
        existing = map(list, zip(*existing))[0]

    return existing


def scrape_offenders():
    """ Scrape all offenders, return as dictionary with databse columns """

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

    # TODO: what if site is not available? try / except
    doc = urllib2.urlopen(DEATH_ROW_URLS['base'] + DEATH_ROW_URLS['executed'])
    table = BeautifulSoup(doc).table

    # Sanity check: do headers match our map?
    headers = [f.string for f in table.find_all('th')]

    for header in exec_table_map.values():
        map_title = header
        table_title = headers.pop(0)

        if table_title != map_title:
            # Looks like format changed, log error & exit
            print '%s Error: Table headers dont match map: %s (map) - %s '\
                '(table)' % (date, map_title, table_title)

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

    return data


def scrape_statement(statement_url):
    """ Scrape statement and return as HTML """
    state_doc = urllib2.urlopen(DEATH_ROW_URLS['base'] + statement_url)
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
        return False
        print '%s Error: Unable to get last statement for %s' %\
            (date, statement_url)
    else:
        return ' '.join([str(t) for t in statement_tags])


def scrape_info_jpg(url, execution_num):
    """ Download image & save to designated directory """

    jpg = urllib2.urlopen(DEATH_ROW_URLS['base'] + url)
    filename = '%s_%s' % (execution_num,
                          url.split('/')[-1])
    with open('%s/%s' % (JPG_INFO_PATH, filename), 'wb') as fp:
        shutil.copyfileobj(jpg, fp)
        return True

    return False


@manager.command
def scrape():
    """ Scrape data from TDCJ and save any new records found
        TODO: Scrape extra offender data. Much of this is in jpg files, so we
              will not be able to get a complete data set.
    """

    #
    # Scrape basic info for all executed offenders
    #

    existing = get_existing_offenders()
    all_offenders = scrape_offenders()

    new_imports = 0
    statement_urls = {}
    info_urls = {}

    for d in all_offenders:
        if int(d['tdcj_id']) not in existing:
            offndr = Offender(**d)
            db.session.add(offndr)
            new_imports += 1

            if offndr.statement_url != 'dr_info/no_last_statement.html':
                statement_urls[offndr.execution_num] = offndr.statement_url

            if '.jpg' in offndr.info_url:
                info_urls[offndr.execution_num] = offndr.info_url

    try:
        db.session.commit()
    except exc:
        print '%s Error: Cannot save records' % date

    #
    # Scrape statements for new offenders
    #

    statements_added = 0
    statements_failed = 0

    for id, url in statement_urls.items():
        statement_text = scrape_statement(url)

        if statement_text is False:
            statements_failed += 1
        else:
            statements_added += 1
            db.session.query(Offender).filter(Offender.id == id).\
                update({Offender.last_statement: statement_text})

    db.session.commit()

    print "%s Notice: Statements added: %d" % (date, statements_added)
    print "%s Notice: Statements failed: %d" % (date, statements_failed)

    #
    # Save jpg files
    #

    if JPG_INFO_PATH is not None:
        info_jpgs_downloaded = 0

        if os.access(JPG_INFO_PATH, os.W_OK):
            for num, url in info_urls.items():
                if scrape_info_jpg(url, num):
                    info_jpgs_downloaded += 1
                else:
                    print '%s Error: Failed to download image from: %s' % \
                        (date, url)
        else:
            print '%s Error: Unable to access JPG_INFO_PATH: %s' % \
                (date, JPG_INFO_PATH)

        print "%s Notice: Info images downloaded: %d" % (date,
                                                         info_jpgs_downloaded)


if __name__ == "__main__":
    manager.run()
