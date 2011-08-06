from codebox import app
from flask import g, redirect, url_for
from functools import wraps

def can_view_org(f):
    @wraps(f)
    def decorated_function(org, *args, **kwargs):
        if not getattr(g, 'user', None) or \
           org not in [o.pk for o in g.user.get_all_organizations()]:
            return redirect(url_for('dashboard'))

        response = app.make_response(f(org, *args, **kwargs))
        response.set_cookie('org', value=org)
        return response
    return decorated_function

def can_admin_org(f):
    @wraps(f)
    def decorated_function(org, *args, **kwargs):
        if not getattr(g, 'user', None) or \
           org not in [o.pk for o in g.user.get_all_organizations(admin=True)]:
            return redirect(url_for('dashboard'))

        response = app.make_response(f(org, *args, **kwargs))
        response.set_cookie('org', value=org)
        return response
    return decorated_function