import hashlib
import time

from codebox import app
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

    def get_owner(self):
        from codebox.apps.auth.models import User

        return User.objects.get(self.owned_by)

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

class PendingMember(Model):
    """
    A member which has been invited and not yet joined,
    or who has applied to join an organization.
    """
    org = String()
    user = String(required=False)
    email = String()
    created_by = String(required=False)
    created_at = Float(default=time.time)
    
    class Meta:
        unique = (('org', 'email'),)
    
    def get_signature(self):
        sig = hashlib.md5(self.email)
        sig.update(app.config['SECRET_KEY'])
        sig = sig.hexdigest()
        
        return sig