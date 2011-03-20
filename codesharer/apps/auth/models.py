from codesharer.utils import yammer
from codesharer.utils.redis import RedisOrderedDict, RedisHashMap, encode_key

YAMMER_KEY = 'kZO991WvBUdApnD6f7g'
YAMMER_SECRET = 'lNLCt5bCQDEXikioA2nhgbIyHln1C6qgON7TdyZA'

class CodeBoxYammer(object):

    def __init__(self):
        self.yammer = yammer.Yammer(YAMMER_KEY, YAMMER_SECRET)

    def create(self, org):
        # save the org specific state here
        pass

    def get_auth_url(self):
        """
        pass this url back to the user to get the
        oauth code to enter into the application
        """
        return self.yammer.get_authorize_url()

    def get_access_token(self, code):
        """
        trade the code for a permanent oauth token and secret
        """
        resp = self.yammer.get_access_token(code)
        if resp.get('oauth_token'):
            # save token information
            print resp.get('oauth_token')
            print resp.get('oauth_token_secret')
