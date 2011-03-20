from codesharer.utils import yammer
from codesharer.utils.models import Model, String
from codesharer.utils.redis import RedisOrderedDict

YAMMER_KEY = 'kZO991WvBUdApnD6f7g'
YAMMER_SECRET = 'lNLCt5bCQDEXikioA2nhgbIyHln1C6qgON7TdyZA'

class User(Model):
    name = String()
    avatar = String(required=False)
    
    def get_all_organizations(self, user):
        from codesharer.apps.organizations.models import OrganizationMember, Organization

        memberships = list(OrganizationMember.objects.for_index('user', user))
        return Organization.objects.get_many([m.org for m in memberships])

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

    def get_oauth_tokens(self):
        return {
            'oauth_token': self.org['oauth_token'],
            'oauth_token_secret': self.org['oauth_token_secret'],
        }

    def save(oauth_token, oauth_token_secret):
        """
        trade the code for a permanent oauth token and secret
        """
        # figure out how to write to redis
        self.org[oauth_token] = oauth_token
        self.org[oauth_token_secret] = oauth_token_secret
        return True
