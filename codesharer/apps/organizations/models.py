import time

from codesharer.utils.models import Model, String, Float

class Organization(Model):
    slug = String()
    name = String()
    created_at = Float(default=time.time)

    def get_all_members(self):
        return OrganizationMember.objects.for_index('org', self.pk)

class OrganizationMember(Model):
    org = String()
    user = String()
    created_at = Float(default=time.time)
    
    class Meta:
        indexes = ('org',)