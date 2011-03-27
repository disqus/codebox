import time

from codesharer.utils.models import Model, String, Float

class Organization(Model):
    name = String()
    email = String()
    domain = String(required=False)
    created_at = Float(default=time.time)

    def get_all_members(self):
        from codesharer.apps.auth.models import User
        
        memberships = list(OrganizationMember.objects.for_index('org', self.pk))
        return User.objects.get_many([m.user for m in memberships])

class OrganizationMember(Model):
    org = String()
    user = String()
    created_at = Float(default=time.time)
    
    class Meta:
        indexes = ('org', 'user')