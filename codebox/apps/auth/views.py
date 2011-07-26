import simplejson as json
import urllib
import urllib2
import urlparse

from codebox.apps.auth.models import User, Profile
from flask import current_app as app, g, request, Blueprint, render_template, redirect, url_for, session

from codebox.apps.organizations.models import Organization, OrganizationMember

auth = Blueprint('auth', __name__)

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
            
            if email:
                domain = urlparse.urlparse(email).hostname
                try:
                    org = Organization.objects.filter(domain=domain)[0]
                except IndexError:
                    pass
                else:
                    if not OrganizationMember.objects.exists(org=org.pk, user=user.pk):
                        OrganizationMember.objects.create(
                            org=org.pk,
                            user=user.pk,
                        )

            g.user = user
            session['userid'] = user.pk

            return redirect(session.get('next') or url_for('snippets.dashboard'))

    return redirect('/')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth/login.html', **{
        'callback_url': url_for('.rpx', _external=True),
    })

@auth.route('/logout')
def logout():
    del session['userid']
    
    return redirect('/')