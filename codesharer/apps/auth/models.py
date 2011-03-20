import uuid
from codesharer.utils import yammer
from codesharer.utils.redis import RedisOrderedDict, RedisHashMap, encode_key

YAMMER_KEY = 'kZO991WvBUdApnD6f7g'
YAMMER_SECRET = 'lNLCt5bCQDEXikioA2nhgbIyHln1C6qgON7TdyZA'

class CodeBoxYammer(object):

    def __init__(self, request, org):
        self.r = request
        self.org = RedisOrderedDict(request, 'auth:org:%s' % org)

    def get_auth_url(self):
        """
        pass this url back to the user to get the
        oauth code to enter into the application
        """
        yammer_api = yammer.Yammer(YAMMER_KEY, YAMMER_SECRET)
        return yammer_api.get_authorize_url()

    def save(oauth_token, oauth_token_secret):
        """
        trade the code for a permanent oauth token and secret
        """
        # figure out how to write to redis
        self.org[oauth_token] = oauth_token
        self.org[oauth_token_secret] = oauth_token_secret
