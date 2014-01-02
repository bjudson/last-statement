from datetime import datetime
import unittest

from index import application as app
import views


class LastStatementTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    #
    # Test helper functions in views
    #

    def test_date2text(self):
        dates = ['12/31/2012', '07/03/2000', '05/12/1983']

        for d in dates:
            date = datetime.strptime(d, '%m/%d/%Y')
            date_text = views.date2text(date)
            date2 = datetime.strptime(date_text, '%d %B %Y')

            assert date == date2

    def test_doy_leap(self):
        dates = {
            '365': datetime.strptime('2000-12-31', '%Y-%m-%d'),
            '365': datetime.strptime('2001-12-31', '%Y-%m-%d'),
            '60': datetime.strptime('2004-02-29', '%Y-%m-%d'),
            '60': datetime.strptime('2004-03-01', '%Y-%m-%d'),
            '59': datetime.strptime('2005-02-28', '%Y-%m-%d'),
            '60': datetime.strptime('2005-03-01', '%Y-%m-%d')
        }

        for doy, date in dates.items():
            doy2 = views.doy_leap(date)

            assert int(doy) == doy2

    #
    # Test data functions
    #

    def test_get_span_totals(self):
        good_types = ['month', 'year']
        bad_types = ['foo', 'day']

        for t in good_types:
            totals = views.get_span_totals(t)
            assert type(totals) == dict and len(totals) > 0

        for t in bad_types:
            totals = views.get_span_totals(t)
            assert type(totals) == dict and len(totals) == 0

    def test_get_colocations(self):
        terms = ['god', 'family']

        for t in terms:
            term_view = views.db.session.query(views.Term).\
                filter(views.Term.title == t).first()
            results = views.get_colocations(term_view)
            assert type(results) == list and len(results) > 0

    def test_statement_time_calc(self):
        good_types = ['month', 'year']
        offenders = views.db.session.query(views.Offender).\
            filter(views.Offender.last_statement != None).\
            limit(10)

        for t in good_types:
            results = views.statement_time_calc(offenders, t)
            assert type(results) == list and len(results) > 0

    #
    # Test public routes
    #

    def test_index(self):
        resp = self.app.get('/')
        assert 'The last statement of' in resp.data

    def test_execution_num(self):
        resp = self.app.get('/execution/1')
        assert 'The last statement of' in resp.data

    def test_all(self):
        resp = self.app.get('/all')
        assert '500. Kimberly McCarthy' in resp.data

    def test_all_text(self):
        resp = self.app.get('/all/text')
        assert 'Love one another' in resp.data

    def test_terms_index(self):
        resp = self.app.get('/terms')
        assert 'chart' in resp.data

    def test_terms_data(self):
        terms = ['god', 'love']

        for t in terms:
            resp = self.app.get('/terms/data/')
            assert 'count' in resp.data

    def test_terms_data_term(self):
        terms = ['god', 'love']

        for t in terms:
            resp = self.app.get('/terms/data/%s' % t)
            assert 'statement' in resp.data
            assert 'count' in resp.data

    #
    # Test admin routes
    #

    # def test_scrape(self):
    #     resp = self.app.get('/admin/scrape')
    #     assert 'Offenders imported:' in resp.data


if __name__ == '__main__':
    unittest.main()
