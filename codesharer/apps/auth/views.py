from flask import current_app as app, g, request, Module, render_template, redirect, url_for

from codesharer.apps.auth.models import CodeBoxYammer
from codesharer.apps.snippets.forms import NewSnippetForm

auth = Module(__name__)

@auth.route('/<org>/verify')
def verify_begin(org):
    yammer_oauth = CodeBoxYammer(request, org)
    return render_template('auth/verify.html', **{
        'url': yammer_oauth.get_auth_url()
    })

@auth.route('/<org>/verify/confirm', methods=['GET', 'POST'])
def verify_complete(org):
    """
    Creates a new snippet for an organization.
    """
    code = form.code.data
    resp = yammer_oauth.get_access_token(code)
    if resp.get('oauth_token') is not None:
        # save to database
        yammer_oauth.save(oauth_token, oauth_token_secret)
