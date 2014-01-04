from flask.ext.testing import TestCase as Base, Twill

from laststatement.wsgi import application as app


class TestCase(Base):

    def create_app(self):
        """Create and return a testing flask app."""

        self.twill = Twill(app, port=3000)
        return app
