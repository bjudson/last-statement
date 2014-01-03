# coding: utf-8

import os
import urllib2
import shutil
import re
import time
from datetime import datetime
from collections import OrderedDict

from bs4 import BeautifulSoup

from flask.ext.script import Manager
from sqlalchemy.orm import exc

from laststatement.wsgi import application as app
from laststatement.models import db, Offender

DEATH_ROW_URLS = {
    'base': 'http://www.tdcj.state.tx.us/death_row/',
    'executed': 'dr_executed_offenders.html',
    'received': 'dr_offenders_on_dr.html'
}

# JPG_INFO_PATH = '%s/%s' % (app.static_folder, 'info_img')
JPG_INFO_PATH = None

os.environ['TZ'] = 'America/Chicago'
time.tzset()

manager = Manager(app)


@manager.command
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

    print "Grabbing data..."

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

    print "Comparing to database..."

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

    print "Statements added: %d" % statements_added

    #
    # Save jpg files
    #

    info_jpgs_downloaded = 0

    if JPG_INFO_PATH is not None:
        if os.access(JPG_INFO_PATH, os.W_OK):
            with_jpg_info = db.session.query(Offender.id,
                                             Offender.execution_num,
                                             Offender.info_url).\
                filter(Offender.info_url.like("%.jpg%"))

            for o in with_jpg_info:
                jpg = urllib2.urlopen(DEATH_ROW_URLS['base'] + o.info_url)
                filename = '%i_%s' % (o.execution_num,
                                      o.info_url.split('/')[-1])
                with open('%s/%s' % (JPG_INFO_PATH, filename), 'wb') as fp:
                    shutil.copyfileobj(jpg, fp)

                info_jpgs_downloaded += 1
        else:
            app.logger.debug('Unable to access JPG_INFO_PATH: %s' %
                             JPG_INFO_PATH)


if __name__ == "__main__":
    manager.run()
