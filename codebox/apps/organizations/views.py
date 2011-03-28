import hashlib

from flask import current_app as app, g, request, Module, render_template, redirect, url_for, flash
from flaskext.mail import Message
from urllib import quote

from codebox.apps.auth.decorators import login_required
from codebox.apps.organizations.forms import NewOrganizationForm, VerifyDomainForm
from codebox.apps.organizations.models import Organization, OrganizationMember, PendingOrganization
from codebox.utils.shortcuts import get_object_or_404
from codebox.utils.text import slugify

orgs = Module(__name__)

@orgs.route('/new', methods=['POST', 'GET'])
@login_required
def new_org():
    form = NewOrganizationForm()
    if form.validate_on_submit():
        is_pending = bool(form.domain.data)
        
        if is_pending:
            org = PendingOrganization.objects.create(
                name=form.name.data,
                lang=form.lang.data,
                domain=form.domain.data,
                created_by=g.user.pk,
            )
            
            return redirect(url_for('verify_domain', org=org.pk))
        else:
            # Generate a unique slug from name
            base_slug = slugify(form.name.data)
            slug = base_slug
            i = 1
            while Organization.objects.exists(slug):
                slug = '%s-%s' % (base_slug, i)
                i += 1
        
            org = Organization.objects.create(
                pk=slug,
                name=form.name.data,
                lang=form.lang.data,
                owned_by=g.user.pk,
            )
            
            OrganizationMember.objects.create(
                org=org.pk,
                user=g.user.pk,
            )

        flash("Your organization was created successfully!")

        return redirect(url_for('list_snippets', org=org.pk))

    return render_template('organizations/new.html', **{
        'form': form,
    })

@orgs.route('/verify/<org>', methods=['POST', 'GET'])
def verify_domain(org):
    porg = get_object_or_404(PendingOrganization, org)
    
    email = request.args.get('e')
    sig = request.args.get('s')
    if all([sig, email]):
        # Generate a unique slug from name
        base_slug = slugify(porg.name)
        slug = base_slug
        i = 1
        while Organization.objects.exists(slug):
            slug = '%s-%s' % (base_slug, i)
            i += 1
    
        org = Organization.objects.create(
            pk=slug,
            name=porg.name,
            lang=porg.lang,
            domain=porg.domain,
            owned_by=porg.created_by,
        )
        
        OrganizationMember.objects.create(
            org=org.pk,
            user=porg.created_by,
        )
        
        flash("Your organization was created successfully!")
        
        return redirect(url_for('list_snippets', org=org.pk))
    
    form = VerifyDomainForm()
    if form.validate_on_submit():
        email = '%s@%s' % (form.email_username.data, porg.domain)
        sig = hashlib.md5(email)
        sig.update(app.config['SECRET_KEY'])
        sig = sig.hexdigest()

        body = render_template('organizations/mail/verify_domain.txt', **{
            'verify_url': '%s?e=%s&s=%s' % (url_for('verify_domain', org=porg.pk, _external=True), quote(email), quote(sig)),
        })
        
        msg = Message("Codebox Domain Verification",
                      sender="verify@codebox.cc",
                      recipients=[email],
                      body=body)
        app.mail.send(msg)
        
        flash("An email has been sent to %s to validate domain ownership." % email)

    return render_template('organizations/verify_domain.html', **{
        'porg': porg,
        'form': form,
    })
    return redirect('/')
