import time
import unittest2

from codesharer.app import create_app
from codesharer.apps.snippets.models import Snippets

class SnippetTestCase(unittest2.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object('codesharer.conf.TestingConfig')
        self.db = self.app.db.connect()
        self.db.flushdb()
        self.client = self.app.test_client()

    def test_snippets(self):
        """
        test snippet creation
        """
        snippets = Snippets(self.db)

        self.assertEquals(len(snippets), 0)

        res = []
        for i in xrange(3):
            time.sleep(0.01)
            res.append(snippets.create(
                org='disqus',
                text='test %d' % i,
                author=1,
            ))

        self.assertEquals(len(snippets), 3)

        res.reverse()

        for n, sn in enumerate(snippets):
            self.assertEquals(res[n], sn)

class SnippetFrontendTestCase(unittest2.TestCase):
    def setUp(self):
        self.app = create_app()
        self.db = self.app.db.connect()
        self.db.flushdb()
        self.client = self.app.test_client()

    def test_snippet_creation(self):
        """
        test snippet creation via post to url
        """
        snippets = Snippets(self.db)

        rv = self.client.post('/disqus/new', data={
            'text': 'foo',
        })
        self.assertEquals(len(snippets), 1)
