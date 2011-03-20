# Ghetto Fixtures

import time
import unittest2

from codesharer.app import create_app
from codesharer.apps.snippets.models import Snippet
from flask import g, Response

app = create_app()
client = app.test_client()
_ctx = app.test_request_context()
_ctx.push()
app.preprocess_request()
g.redis.flushdb()

# Create sample snippets
# plaintext
Snippet.objects.create(org='disqus', user=1, lang=1, text = "Hello World!")
# python
Snippet.objects.create(org='disqus', user=1, lang=1, text = "print 'cramer sucks'")
# html
Snippet.objects.create(org='disqus', user=1, lang=1, text = '<h1>Cramer sucks</h1>')
# javascript
Snippet.objects.create(org='disqus', user=1, lang=1, text = "document.write('cramer sucks')")


