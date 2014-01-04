import unittest
import json

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

    def test_executions_service(self):
        resp = self.client.get('/api/1/executions/1')
        self.assert200(resp)

    def test_terms_service(self):
        resp = self.client.get('/api/1/terms/5')
        assert resp.status == '302 FOUND'
        assert True

    def test_terms_data(self):
        resp = self.client.get('/api/1/terms/data/')
        self.assert200(resp)

    def test_terms_data_single(self):
        resp = self.client.get('/api/1/terms/data/love')
        self.assert200(resp)

        data = json.loads(resp.data)
        assert len(data['months']) > 0
        assert len(data['statements']) > 0

if __name__ == '__main__':
    unittest.main()
