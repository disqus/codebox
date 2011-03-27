import time

from codebox.utils.models import Model, String, Float, Boolean

class User(Model):
    name = String()
    email = String(required=False)
    avatar = String(required=False)
    created_at = Float(default=time.time)

    class Meta:
        indexes = ('user',)

    def get_all_organizations(self):
        from codebox.apps.organizations.models import OrganizationMember, Organization

        memberships = list(OrganizationMember.objects.for_index('user', self.pk))
        return Organization.objects.get_many([m.org for m in memberships])

    def get_relation(self, relation):
        return list(relation.objects.for_index('user', self.pk))

class Email(Model):
    user = String()
    email = String()
    verified = Boolean(default=False)
    
    class Meta:
        indexes = ('user',)

class Profile(Model):
    user = String()
    created_at = Float(default=time.time)
    
    class Meta:
        indexes = ('user',)