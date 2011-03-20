try:
    import json
except ImportError:
    import simplejson as json
import time
import urllib
import urlparse
import oauth2 as oauth

class Endpoint(object):
    def __init__(self, yammer):
        self.yammer = yammer

    def _get(self, endpoint, **params):
        return self.yammer._apicall(endpoint, 'GET', **params)

    def _post(self, endpoint, **params):
        return self.yammer._apicall(endpoint, 'POST', **params)

    def _delete(self, endpoint, **params):
        return self.yammer._apicall(endpoint, 'DELETE', **params)


class MessageEndpoint(Endpoint):

    def _get_msgs(self, endpoint, raw, older_than, newer_than, threaded):
        msgs = self._get(endpoint, older_than=older_than,
                         newer_than=newer_than, threaded=threaded)
        if raw:
            return msgs
        else:
            if 'messages' not in msgs:
                print msgs
            return msgs['messages']

    def all(self, raw=False, older_than=None, newer_than=None, threaded=None):
        return self._get_msgs('messages', raw=raw,
                              older_than=older_than, newer_than=newer_than,
                              threaded=threaded)

    def sent(self, raw=False, older_than=None, newer_than=None, threaded=None):
        return self._get_msgs('messages/sent', raw=raw,
                              older_than=older_than, newer_than=newer_than,
                              threaded=threaded)

    def received(self, raw=False, older_than=None, newer_than=None, threaded=None):
        return self._get_msgs('messages/received', raw=raw,
                              older_than=older_than, newer_than=newer_than,
                              threaded=threaded)

    def following(self, raw=False, older_than=None, newer_than=None, threaded=None):
        return self._get_msgs('messages/following', raw=raw,
                              older_than=older_than, newer_than=newer_than,
                              threaded=threaded)

    def from_user(self, id, raw=False, older_than=None, newer_than=None, threaded=None):
        return self._get_msgs('messages/from_user/%s' % id, raw=raw,
                              older_than=older_than, newer_than=newer_than,
                              threaded=threaded)

    def from_bot(self, id, raw=False, older_than=None, newer_than=None, threaded=None):
        return self._get_msgs('messages/from_bot/%s' % id, raw=raw,
                              older_than=older_than, newer_than=newer_than,
                              threaded=threaded)

    def tagged_with(self, id, raw=False, older_than=None, newer_than=None, threaded=None):
        return self._get_msgs('messages/tagged_with/%s' % id, raw=raw,
                              older_than=older_than, newer_than=newer_than,
                              threaded=threaded)

    def in_group(self, id, raw=False, older_than=None, newer_than=None, threaded=None):
        return self._get_msgs('messages/in_group/%s' % id, raw=raw,
                              older_than=older_than, newer_than=newer_than,
                              threaded=threaded)

    def favorites_of(self, id, raw=False, older_than=None, newer_than=None, threaded=None):
        return self._get_msgs('messages/favorites_of/%s' % id, raw=raw,
                              older_than=older_than, newer_than=newer_than,
                              threaded=threaded)

    def in_thread(self, id, raw=False, older_than=None, newer_than=None, threaded=None):
        return self._get_msgs('messages/in_thread/%s' % id, raw=raw,
                              older_than=older_than, newer_than=newer_than,
                              threaded=threaded)

    def post(self, body, group_id=None, replied_to_id=None, direct_to_id=None):
        # doesn't support attachments
        return self._post('messages/', group_id=group_id,
                          replied_to_id=replied_to_id, body=body,
                          direct_to_id=direct_to_id)

    def delete(self, message_id):
        return self._delete('messages/%s' % message_id)

class GroupEndpoint(Endpoint):

    def all(self, page=1, letter=None, sort_by=None, reverse=None):
        return self._get('groups', page=page, letter=letter, sort_by=sort_by,
                         reverse=reverse)

    def get(self, id):
        return self._get('groups/%s' % id)

    def create(self, name, private=None):
        return self._post('groups', name=name, private=private)

    def update(self, id, name, private):
        return self._post('groups/%s' % id, name=name, private=private)

class UserEndpoint(Endpoint):

    def all(self, page=1, letter=None, sort_by=None, reverse=None):
        return self._get('users', page=page, letter=letter, sort_by=sort_by,
                         reverse=reverse)

    def get(self, id):
        return self._get('users/%s' % id)

    def current(self):
        return self._get('users/current')

    def by_email(self, email):
        return self._get('users/by_email', email=email)


class RelationshipsEndpoint(Endpoint):

    def get(self, id):
        return self._get('relationships/%s' % id)

    def post(self, id, subordinate=None, superior=None, colleague=None):
        return self._post('relationships', user_id=id, subordinate=subordinate, superior=superior,colleague=colleage)

class Yammer(object):
    request_token_url = 'https://www.yammer.com/oauth/request_token'
    access_token_url = 'https://www.yammer.com/oauth/access_token'
    authorize_url = 'https://www.yammer.com/oauth/authorize'
    base_url = 'https://www.yammer.com/api/v1/'

    def __init__(self, consumer_key, consumer_secret, oauth_token=None, oauth_token_secret=None):
        self.consumer = oauth.Consumer(consumer_key, consumer_secret)
        if oauth_token and oauth_token_secret:
            self.token = oauth.Token(oauth_token, oauth_token_secret)
        else:
            self.token = None
        self.client = oauth.Client(self.consumer, self.token)

        # connect endpoints
        self.messages = MessageEndpoint(self)
        self.groups = GroupEndpoint(self)
        self.users = UserEndpoint(self)
        self.relationships = RelationshipEndpoint(self)

    # authorization
    @property
    def request_token(self):
        if not hasattr(self, '_request_token'):
            resp, content = self.client.request(self.request_token_url, "GET")
            if resp['status'] != '200':
                raise Exception("Invalid response %s." % resp['status'])

            self._request_token = dict(urlparse.parse_qsl(content))
        return self._request_token

    def get_authorize_url(self):
        return "%s?oauth_token=%s" % (self.authorize_url, self.request_token['oauth_token'])

    def get_access_token(self, oauth_verifier):
        # set verifier
        token = oauth.Token(self.request_token['oauth_token'],
                            self.request_token['oauth_token_secret'])
        token.set_verifier(oauth_verifier)
        self.client = oauth.Client(self.consumer, token)

        # parse response
        resp, content = self.client.request(self.access_token_url, "POST")
        access_token = dict(urlparse.parse_qsl(content))
        return access_token

    # requests
    def _apicall(self, endpoint, method, **params):
        if method == 'GET':
            suffix = '.json'
        else:
            suffix = ''
        url = '%s%s%s' % (self.base_url, endpoint, suffix)
        body = None
        cleaned_params = dict([(k,v) for k,v in params.iteritems() if v])

        if cleaned_params:
            body = urllib.urlencode(cleaned_params)
            if method == 'GET':
                url = '%s?%s' % (url, body)
                body = None

        resp, content = self.client.request(url, method=method, body=body)
        try:
            json_obj = json.loads(content)
            if 'response' in json_obj and json_obj['response'].get('stat', None) == 'fail':
                raise Exception(json_obj['response']['message'])
            return json_obj
        except ValueError:
            print resp, content
