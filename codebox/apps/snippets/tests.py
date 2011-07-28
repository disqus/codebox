import time
import unittest2

from codebox import app
from codebox.apps.snippets.models import Snippet
from codebox.apps.organizations.models import Organization
from flask import g, Response

class FlaskTest(unittest2.TestCase):
    def setUp(self):
        self.app = app
        self.app.config.from_object('codebox.conf.TestingConfig')
        self.client = self.app.test_client()
        
        self._ctx = self.app.test_request_context()
        self._ctx.push()
        self.app.preprocess_request()

        g.redis.flushdb()

    def tearDown(self):
        self.app.process_response(Response())
        self._ctx.pop()

class SnippetTestCase(FlaskTest):
    def test_snippets(self):
        """Basic api test of model"""
        self.assertEquals(Snippet.objects.count(), 0)
    
        Organization.objects.create(
            pk='disqus',
            name='DISQUS',
        )
    
        res = []
        for i in xrange(3):
            time.sleep(0.01)
            res.append(Snippet.objects.create(
                org='disqus',
                text='test %d' % i,
                user=1,
                lang='python',
            ))

        self.assertEquals(Snippet.objects.count(), 3)
    
        self.assertEquals(len(list(Snippet.objects.filter(org='disqus'))), 3)
    
        res.reverse()
    
        for n, sn in enumerate(Snippet.objects.all()):
            self.assertEquals(res[n], sn)
            self.assertEquals(res[n], Snippet.objects.get(sn.pk))
 
# class SnippetFrontendTestCase(FlaskTest):
#     def test_snippet_creation(self):
#         """
#         test snippet creation via post to url
#         """
#         rv = self.client.post('/disqus/new', data={
#             'text': 'foo',
#         })
#         self.assertEquals(Snippet.objects.count(), 1)
