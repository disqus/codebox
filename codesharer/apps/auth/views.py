from flask import current_app as app, g, request, Module, render_template, redirect, url_for, session, flash

from codesharer.apps.auth.models import YammerOAuth, User
from codesharer.apps.auth.forms import NewAuthForm, LoginForm

from codesharer.apps.organizations.models import Organization, OrganizationMember

from codesharer.utils import pypodio

auth = Module(__name__)

@auth.route('/<org>/login', methods=['GET', 'POST'])
def org_login(org):

    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = form.username.data
        password = form.password.data
        # login with podio
        # TODO: move this somewhere else
        podio = pypodio.Podio(
            client_id = app.config['PODIO_CLIENT_ID'],
            client_secret = app.config['PODIO_KEY'],
        )
        podio.request_oauth_token(user, password)

        profile = podio.users_get_active_profile()
        podio_org = str(profile['organization']).lower()
        podio_id = profile['user_id']
        podio_name = profile['name']
        try:
            user = User.objects.get(podio_id)
        except User.DoesNotExist:
            user = User.objects.create(pk=podio_id, name=podio_name)
        try:
            org = Organization.objects.get(podio_org)
        except Organization.DoesNotExist:
            org = Organization.objects.create(pk=podio_org, name="DISQUS")
        try:
            m2m = OrganizationMember.objects.get(podio_org+str(podio_id))
        except OrganizationMember.DoesNotExist:
            m2m = OrganizationMember.objects.create(pk=podio_org+str(podio_id), org=podio_org, user = podio_id)
        
        g.user = user
        session.userid = user.pk

        flash('Welcome to CodeBox')

        return redirect(url_for('dashboard'))
        
        
    else:
        profile = None
        
    return render_template('auth/login.html', **{
            'org': org,
            'form': form,
            })

@auth.route('/<org>/verify')
def verify_begin(org):

    yammer_oauth = YammerOAuth.objects.create(pk=org, org=org)
    url = yammer_oauth.get_auth_url()

    print 'url', url

    form = NewAuthForm()

    return render_template('auth/verify.html', **{
        'url': url,
        'form': form,
        'org': org,
    })

@auth.route('/<org>/verify/confirm', methods=['GET', 'POST'])
def verify_complete(org):
    """
    Creates a new snippet for an organization.
    """
    yammer_oauth = YammerOAuth.objects.get(org)
    code = request.form['code']
    yammer_api = session['yammer_api']
    resp = yammer_api.get_access_token(code)
    if 'oauth_token' in resp:
        yammer_oauth.save(resp['oauth_token'], resp['oauth_token_secret'])
        return redirect(url_for('dashboard'))
