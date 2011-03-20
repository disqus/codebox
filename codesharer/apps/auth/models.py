import time

from codesharer.utils import yammer
from codesharer.utils.models import Model, String, Float
from flask import session

YAMMER_KEY = 'kZO991WvBUdApnD6f7g'
YAMMER_SECRET = 'lNLCt5bCQDEXikioA2nhgbIyHln1C6qgON7TdyZA'

class YammerOAuth(Model):

    org = String()
    created_at = Float(default=time.time)
    oauth_token = String(required=False)
    oauth_token_secret = String(required=False)

    def get_auth_url(self):
        """
        pass this url back to the user to get the
        oauth code to enter into the application
        """
        if 'yammer_api' not in session:
            session['yammer_api'] = yammer.Yammer(YAMMER_KEY, YAMMER_SECRET)
        yammer_api = session['yammer_api']
        return yammer_api.get_authorize_url()

    def get_access_token(self, code):
        if 'yammer_api' not in session:
            session['yammer_api'] = yammer.Yammer(YAMMER_KEY, YAMMER_SECRET)
        yammer_api = session['yammer_api']
        return yammer_api.get_access_token(code)

    def get_oauth_tokens(self):
        return {
            'oauth_token': self.oauth_token,
            'oauth_token_secret': self.oauth_token_secret,
        }

    def save(self, oauth_token, oauth_token_secret):
        """
        trade the code for a permanent oauth token and secret
        """
        # figure out how to write to redis
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
