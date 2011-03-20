import time

from codesharer.utils.models import Model, String, Float

class Snippet(Model):
    org = String()
    author = String()
    text = String()
    created_at = Float(default=time.time)

    class Meta:
        indexes = ('org', 'author')
