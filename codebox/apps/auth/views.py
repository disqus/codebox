import simplejson as json
import urllib
import urllib2

from codebox.apps.auth.decorators import login_required
from codebox.apps.auth.models import User, Profile, Email
from flask import current_app as app, g, request, Module, render_template, redirect, url_for, session, flash

# from codebox.apps.organizations.models import Organization, OrganizationMember

auth = Module(__name__)

@auth.route('/rpx', methods=['POST'])
def rpx():
    token = request.form.get('token')

    if token:
        params = {
            'token': token,
            'apiKey': app.config['JANRAIN_API_KEY'],
            'format': 'json',
        }

        response = urllib2.urlopen('https://rpxnow.com/api/v2/auth_info',
                                   urllib.urlencode(params))

        auth_info = json.loads(response.read())

        if auth_info['stat'] == 'ok':
            profile = auth_info['profile']

            identifier = profile['identifier']

            name = profile.get('displayName') or ''
            email = profile.get('email') or ''
            avatar = profile.get('photo') or ''

            try:
                profile = Profile.objects.get(identifier)
                user = User.objects.get(profile.user)
            except Profile.DoesNotExist:
                user = User.objects.create(
                    name=name or identifier,
                    email=email,
                    avatar=avatar,
                )
                profile = Profile.objects.create(
                    pk=identifier,
                    user=user.pk,
                )

            # try:
            #     org = Organization.objects.get(podio_org)
            # except Organization.DoesNotExist:
            #     org = Organization.objects.create(pk=podio_org, name="DISQUS")
            # try:
            #     m2m = OrganizationMember.objects.get(podio_org+str(podio_id))
            # except OrganizationMember.DoesNotExist:
            #     m2m = OrganizationMember.objects.create(pk=podio_org+str(podio_id), org=podio_org, user = podio_id)

            g.user = user
            session['userid'] = user.pk

            flash('Welcome to CodeBox')

            return redirect(url_for('dashboard'))

    return redirect('/')

@auth.route('/login', methods=['GET', 'POST'])
def login():        
    return render_template('auth/login.html', **{
        'callback_url': url_for('rpx', _external=True),
    })
