import time

from codesharer.utils.models import Model, String, Float
from codesharer.apps.auth.models import User

LANGUAGES = {
    'py': 'python',
    'js': 'javascript',
    'html': 'html',
}

class Snippet(Model):
    org = String()
    user = String()
    text = String()
    lang = String()
    created_at = Float(default=time.time)

    class Meta:
        indexes = ('org', 'author')
