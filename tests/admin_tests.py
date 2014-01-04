import unittest

from tests import TestCase
from laststatement.admin import views


class LastStatementApiTestCase(TestCase):

    #
    # Functions
    #

    def test_load_user(self):
        user = views.load_user(1)
        assert user.email is not None

    #
    # Routes
    #

if __name__ == '__main__':
    unittest.main()
