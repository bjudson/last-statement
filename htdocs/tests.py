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

if __name__ == '__main__':
    unittest.main()
