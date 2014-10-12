import unittest

from tests import TestCase
from laststatement.admin import views


class LastStatementAdminTestCase(TestCase):

    #
    # Functions
    #

    def test_load_user(self):
        user = views.load_user(1)
        assert user.email is not None

    #
    # Routes
    #

    def test_admin_index(self):
        resp = self.client.get('/admin', follow_redirects=True)
        self.assert200(resp)

    def test_admin_login(self):
        resp = self.client.get('/login', follow_redirects=True)
        self.assert200(resp)

if __name__ == '__main__':
    unittest.main()
