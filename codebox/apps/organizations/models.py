import time

from codebox.utils.models import Model, String, Float, Boolean

class Organization(Model):
    name = String()
    lang = String(required=False)
    domain = String(required=False)
    owned_by = String(required=False) # fkey to User
    created_at = Float(default=time.time)

    class Meta:
        unique = (('domain',),)

    def get_all_members(self):
        from codebox.apps.auth.models import User
        
        memberships = list(OrganizationMember.objects.filter(org=self.pk))
        return User.objects.get_many([m.user for m in memberships])

class OrganizationMember(Model):
    org = String()
    user = String()
    verified = Boolean(default=False)
    created_at = Float(default=time.time)
    
    class Meta:
        index = (('org',), ('user',))
        unique = (('org', 'user'),)

class PendingOrganization(Model):
    """
    An organization pending a domain verification.
    """
    name = String()
    lang = String(required=False)
    domain = String()
    created_by = String(required=False) # fkey to User
    created_at = Float(default=time.time)
