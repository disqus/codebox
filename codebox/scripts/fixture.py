# Ghetto Fixtures

from codebox import app
from codebox.apps.auth.models import User
from codebox.apps.snippets.models import Snippet
from codebox.apps.organizations.models import Organization, OrganizationMember
from flask import g

client = app.test_client()
_ctx = app.test_request_context()
_ctx.push()
app.preprocess_request()
g.redis.flushdb()

User.objects.create(pk=1, name='zeeg')

Organization.objects.create(pk='disqus', name='DISQUS')

OrganizationMember.objects.create(org='disqus', user=1)

# Create sample snippets

# plaintext
Snippet.objects.create(org='disqus', user=1, lang='text', text = "Hello World!")
# python
Snippet.objects.create(org='disqus', user=1, lang='python', text = "print 'Disqus was here'")
# html
Snippet.objects.create(org='disqus', user=1, lang='html', text = '<h1>Look its HTML!</h1>')
# javascript
Snippet.objects.create(org='disqus', user=1, lang='javascript', text = "document.write('Di-squs')")

