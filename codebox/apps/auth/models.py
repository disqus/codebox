import time

from codebox.utils import yammer
from codebox.utils.models import Model, String, Float

from flask import session

class User(Model):
    name = String()
    email = String(required=False)
    avatar = String(required=False)
    created_at = Float(default=time.time)
    
    def get_all_organizations(self, user):
        from codebox.apps.organizations.models import OrganizationMember, Organization

        memberships = list(OrganizationMember.objects.for_index('user', user))
        return Organization.objects.get_many([m.org for m in memberships])

class Profile(Model):
    user = String()
    created_at = Float(default=time.time)
    
    class Meta:
        indexes = ('user',)