from codesharer.utils.models import Model, String

class Organization(Model):
    slug = String()
    name = String()

    def get_all_members(self):
        return OrganizationMember.objects.for_index('org', self.pk)

class OrganizationMember(Model):
    org = String()
    user = String()
    
    class Meta:
        indexes = ('org',)