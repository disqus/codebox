from flask import g, redirect, request
from functools import wraps

from codebox.apps.organizations.models import OrganizationMember

def can_view_org(f):
    @wraps(f)
    def decorated_function(org, *args, **kwargs):
        if not getattr(g, 'user', None) or \
           org not in [o.pk for o in g.user.get_all_organizations()]:
            return redirect('/')
        return f(org, *args, **kwargs)
    return decorated_function