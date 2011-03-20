import unittest2

from flask import url_for
from codesharer.app import create_app
from codesharer.apps.snippets.models import Snippets

class SnippetTestCase(unittest2.TestCase):
    def setUp(self):
        self.app = create_app()
        self.db = self.app.db.connect()
        self.db.flush()
        self.client = self.app.test_client()
    
    def test_snippets(self):
        """
        Simplest test we can do. Train using ours and train using the built-in.
        """
        snippets = Snippets(self.db)
        
        self.assertEquals(len(snippets), 0)
        
        snippets.create(text='test')

        self.assertEquals(len(snippets), 1)

class SnippetFrontendTestCase(unittest2.TestCase):
    def setUp(self):
        self.app = create_app()
        self.db = self.app.db.connect()
        self.db.flush()
        self.client = self.app.test_client()
    
    def test_snippet_creation(self):
        """
        Simplest test we can do. Train using ours and train using the built-in.
        """
        snippets = Snippets(self.db)
        
        rv = self.client.post('/disqus/new', data={
            'text': 'foo',
        })
        self.assertEquals(len(snippets), 1)
