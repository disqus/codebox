import time
import unittest2

from codesharer.app import create_app
from codesharer.apps.snippets.models import Snippet
from flask import g, Response

class SnippetTestCase(unittest2.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object('codesharer.conf.TestingConfig')
        self.client = self.app.test_client()
        
        self._ctx = self.app.test_request_context()
        self._ctx.push()
        self.app.preprocess_request()

        g.redis.flushdb()

    def tearDown(self):
        self.app.process_response(Response())
        self._ctx.pop()
    
    def test_snippets(self):
        """
        Simplest test we can do. Train using ours and train using the built-in.
        """            
        self.assertEquals(Snippet.objects.count(), 0)
    
        res = []
        for i in xrange(3):
            time.sleep(0.01)
            res.append(Snippet.objects.create(
                org='disqus',
                text='test %d' % i,
                author=1,
            ))

        self.assertEquals(Snippet.objects.count(), 3)
    
        res.reverse()
    
        for n, sn in enumerate(Snippet.objects.all()):
            self.assertEquals(res[n], sn)

class SnippetFrontendTestCase(unittest2.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object('codesharer.conf.TestingConfig')
        self.db = self.app.db.connect()
        self.db.flushdb()
        self.client = self.app.test_client()

    def test_snippet_creation(self):
        """
        test snippet creation via post to url
        """
        rv = self.client.post('/disqus/new', data={
            'text': 'foo',
        })
        self.assertEquals(Snippet.objects.count(), 1)
