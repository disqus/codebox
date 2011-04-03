import time

from codebox.utils.models import Model, String, Float
from codebox.apps.auth.models import User

LANGUAGES = {
    'py': 'python',
    'js': 'javascript',
    'html': 'html',
}

class Snippet(Model):
    org = String()
    user = String()
    text = String()
    keywords = String(required=False)
    lang = String()
    created_at = Float(default=time.time)

    languages = [
        ('text', 'Plaintext'),
        ('javascript', 'JavaScript'),
        ('html', 'HTML'),
        ('python', 'Python'),
        ('ruby', 'Ruby'),
        ('c', 'C'),
        ('java', 'Java'),
        ('xml', 'XML'),
        ('css', 'CSS'),
    ]

    class Meta:
        index = (('org',), ('user',))

    def post_create(self):
        from codebox.apps.organizations.models import Organization
        # Fill our dashboard index
        for user in Organization.objects.get(self.org).get_all_members():
            Snippet.objects.add_to_index(self.pk, dashboard=user.pk)
    
    def get_user(self):
        return User.objects.get(self.user)