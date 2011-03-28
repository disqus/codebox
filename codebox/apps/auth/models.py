import time

from codebox.utils.models import Model, String, Float, Boolean

class User(Model):
    name = String()
    email = String(required=False)
    avatar = String(required=False)
    created_at = Float(default=time.time)

    class Meta:
        index = (('user',),)
        unique = (('email',))

    def get_all_organizations(self):
        from codebox.apps.organizations.models import OrganizationMember, Organization

        memberships = list(OrganizationMember.objects.filter(user=self.pk))
        return Organization.objects.get_many([m.org for m in memberships])

    def get_relation(self, relation):
        return list(relation.objects.filter(user=self.pk))

class Email(Model):
    user = String()
    email = String()
    verified = Boolean(default=False)
    
    class Meta:
        index = (('user',),)
        unique = (('email',))

class Profile(Model):
    user = String()
    created_at = Float(default=time.time)
    
    class Meta:
        index = (('user',),)
