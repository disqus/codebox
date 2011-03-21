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
        indexes = ('org', 'user')

    def post_create(self):
        from codesharer.apps.organizations.models import Organization
        # Fill our dashboard index
        for user in Organization.objects.get(self.org).get_all_members():
            Snippet.objects.add_to_index('dashboard', user.pk, self.pk)
            