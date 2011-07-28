import simplejson as json
import urllib
import urllib2
import urlparse
import uuid

from flask import g, request, render_template, redirect, url_for, session, \
                  flash

from codebox import app
from codebox.apps.auth.forms import EditProfileForm
from codebox.apps.auth.models import User, Profile
from codebox.apps.auth.decorators import login_required
from codebox.apps.organizations.models import Organization, OrganizationMember

@app.route('/rpx', methods=['POST'])
def rpx():
    token = request.form.get('token')

    if not token:
        return redirect('/')

    params = {
        'token': token,
        'apiKey': app.config['JANRAIN_API_KEY'],
        'format': 'json',
    }

    response = urllib2.urlopen('https://rpxnow.com/api/v2/auth_info',
                               urllib.urlencode(params))

    auth_info = json.loads(response.read())

    if auth_info['stat'] != 'ok':
        return redirect('/')
    
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
        if domain:
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

    return redirect(session.get('next') or url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth/login.html', **{
        'callback_url': url_for('rpx', _external=True),
    })

@app.route('/logout')
def logout():
    del session['userid']
    
    return redirect('/')

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if not g.user.api_token:
        g.user.api_token = uuid.uuid4().hex
    
    form = EditProfileForm(name=g.user.name)
    if form.validate_on_submit():
        if form.update_token.data:
            g.user.api_token = uuid.uuid4().hex
        g.user.name = form.name.data

        flash("Your profile was updated successfully!")

        return redirect(url_for('edit_profile'))

    return render_template('auth/edit_profile.html', **{
        'form': form,
    })