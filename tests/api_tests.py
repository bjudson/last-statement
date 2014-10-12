import unittest
import json
from datetime import datetime

from tests import TestCase
from laststatement.api import views


class LastStatementApiTestCase(TestCase):

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
        term_view = views.db.session.query(views.Term).first()
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
    # Routes
    #

    def test_index(self):
        resp = self.client.get('/api/1/')
        self.assert200(resp)

    def test_executions_service_all(self):
        resp = self.client.get('/api/1/executions')
        self.assert200(resp)

        data = json.loads(resp.data)
        assert len(data['executions']) == data['count']
        assert len(data['errors']) == 0

    def test_executions_service_filter_name(self):
        last_name = 'Barefoot'
        first_name = 'Thomas'
        resp = self.client.get('/api/1/executions?name=%s,%s' %
                               (last_name, first_name))
        self.assert200(resp)

        data = json.loads(resp.data)
        assert len(data['executions']) == data['count']
        assert len(data['errors']) == 0
        for e in data['executions']:
            assert e['first_name'] == first_name
            assert e['last_name'] == last_name

        resp = self.client.get('/api/1/executions?name=%s' %
                               (last_name))
        self.assert200(resp)

        data = json.loads(resp.data)
        assert len(data['executions']) == data['count']
        assert len(data['errors']) == 0
        for e in data['executions']:
            assert e['last_name'] == last_name

    def test_executions_service_filter_age(self):
        ages = [25, 40]
        resp = self.client.get('/api/1/executions?age_lt=%d' % ages[1])
        self.assert200(resp)

        data = json.loads(resp.data)
        assert len(data['executions']) == data['count']
        assert len(data['errors']) == 0
        for e in data['executions']:
            assert e['age'] < ages[1]

        resp = self.client.get('/api/1/executions?age_gt=%d' % ages[0])
        self.assert200(resp)

        data = json.loads(resp.data)
        assert len(data['executions']) == data['count']
        assert len(data['errors']) == 0
        for e in data['executions']:
            assert e['age'] > ages[0]

        resp = self.client.get('/api/1/executions?age_gt=%d&age_lt=%d' %
                               (ages[0], ages[1]))
        self.assert200(resp)

        data = json.loads(resp.data)
        assert len(data['executions']) == data['count']
        assert len(data['errors']) == 0
        for e in data['executions']:
            assert e['age'] > ages[0]
            assert e['age'] < ages[1]

    def test_executions_service_filter_date(self):
        today = datetime.now()
        today_str = today.strftime('%Y-%m-%d')
        millenium = datetime(2000, 1, 1)
        millenium_str = datetime(2000, 1, 1).strftime('%Y-%m-%d')

        resp = self.client.get('/api/1/executions?until=%s' % today_str)
        self.assert200(resp)

        data = json.loads(resp.data)
        assert len(data['executions']) == data['count']
        assert len(data['errors']) == 0
        assert len(data['executions']) > 100
        for e in data['executions']:
            date = datetime.strptime(e['execution_date'], '%Y-%m-%d')
            assert date < today

        resp = self.client.get('/api/1/executions?since=%s' % millenium_str)
        self.assert200(resp)

        data = json.loads(resp.data)
        assert len(data['executions']) == data['count']
        assert len(data['errors']) == 0
        assert len(data['executions']) > 10
        for e in data['executions']:
            date = datetime.strptime(e['execution_date'], '%Y-%m-%d')
            assert date > millenium

    def test_executions_service_filter_race(self):
        resp = self.client.get('/api/1/executions?race=w')
        self.assert200(resp)

        data = json.loads(resp.data)
        assert len(data['executions']) == data['count']
        assert len(data['errors']) == 0
        for e in data['executions']:
            assert e['race'] == 'White'

    def test_executions_service_single(self):
        resp = self.client.get('/api/1/executions/1')
        self.assert200(resp)

        data = json.loads(resp.data)
        assert len(data['executions']) == data['count']
        assert len(data['errors']) == 0

    def test_terms_data(self):
        resp = self.client.get('/api/1/terms/data/')
        self.assert200(resp)

    def test_terms_data_single(self):
        resp = self.client.get('/api/1/terms/data/love')
        self.assert200(resp)

        data = json.loads(resp.data)
        assert len(data['months']) > 0
        assert len(data['statements']) > 0

    def test_sentiments_all(self):
        resp = self.client.get('/api/1/sentiments/all')
        self.assert200(resp)

        data = json.loads(resp.data)
        assert len(data['sentiments']) > 0
        assert data['sentiments'][0]['active'] is True
        assert data['sentiments'][0]['execution_count'] > 0
        assert data['sentiments'][0]['execution_count'] == \
            len(data['sentiments'][0]['executions'])

    def test_sentiments_single(self):
        id = 1
        resp = self.client.get('/api/1/sentiments/%d' % id)
        self.assert200(resp)

        data = json.loads(resp.data)
        assert data['sentiment']['id'] == id

if __name__ == '__main__':
    unittest.main()
