import time

from codebox.utils.models import Model, String, Float, Boolean

class User(Model):
    name = String()
    email = String(required=False)
    avatar = String(required=False)
    created_at = Float(default=time.time)
    api_token = String(required=False)

    class Meta:
        unique = (('email',), ('api_token',))

    def get_all_organizations(self, admin=False):
        from codebox.apps.organizations.models import OrganizationMember, Organization

        memberships = list(OrganizationMember.objects.filter(user=self.pk))
        orgs = Organization.objects.get_many([m.org for m in memberships])
        if admin:
            orgs = filter(lambda x: x.owned_by == self.pk, orgs)
        return orgs

    def can_admin_org(self, org):
        return org.owned_by == self.pk

    def get_relation(self, relation):
        return list(relation.objects.filter(user=self.pk))

class Email(Model):
    user = String()
    email = String()
    verified = Boolean(default=False)
    
    class Meta:
        index = (('user',),)
        unique = (('email',),)

class Profile(Model):
    user = String()
    created_at = Float(default=time.time)
    
    class Meta:
        index = (('user',),)
