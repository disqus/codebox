import hashlib

from flask import g, request, render_template, redirect, url_for, flash
from flaskext.mail import Message
from urllib import quote

from codebox import app, mail
from codebox.apps.auth.decorators import login_required
from codebox.apps.auth.models import User
from codebox.apps.organizations.decorators import can_admin_org, can_view_org
from codebox.apps.organizations.forms import NewOrganizationForm, VerifyDomainForm, InviteUserForm, \
                                             EditOrganizationForm
from codebox.apps.organizations.models import Organization, OrganizationMember, PendingOrganization, \
                                              PendingMember
from codebox.apps.snippets.models import Snippet
from codebox.utils.shortcuts import get_object_or_404
from codebox.utils.text import slugify

@app.route('/new', methods=['POST', 'GET'])
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

@app.route('/<org>/edit', methods=['POST', 'GET'])
@login_required
def edit_org(org):
    org = get_object_or_404(Organization, org)

    form = EditOrganizationForm(name=org.name, lang=org.lang)
    if form.validate_on_submit():
        org.name = form.name.data
        org.lang = form.lang.data

        flash("Your organization was updated successfully!")

        return redirect(url_for('list_snippets', org=org.pk))

    return render_template('organizations/edit.html', **{
        'form': form,
        'org': org,
    })

@app.route('/<org>/details')
@login_required
@can_view_org
def org_details(org):
    org = get_object_or_404(Organization, org)
    if not g.user.can_admin_org(org):
        return redirect(url_for('org_snippets', org=org.pk))

    return render_template('organizations/details.html', **{
        'org': org,
    })

@app.route('/verify/<org>', methods=['POST', 'GET'])
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
        
        app.logger.info("Sending domain verification to %s", email)

        body = render_template('organizations/mail/verify_domain.txt', **{
            'verify_url': '%s?e=%s&s=%s' % (url_for('verify_domain', org=porg.pk, _external=True), quote(email), quote(sig)),
        })
        
        msg = Message("Codebox Domain Verification",
                      recipients=[email],
                      body=body)
        mail.send(msg)
        
        flash("An email has been sent to %s to validate domain ownership." % email)

    return render_template('organizations/verify_domain.html', **{
        'porg': porg,
        'form': form,
    })
    return redirect('/')

@app.route('/<org>/invite/confirm/<pmem>/<sig>', methods=['POST', 'GET'])
@login_required
def invite_confirm(org, pmem, sig):
    org = get_object_or_404(Organization, org)
    pmem = get_object_or_404(PendingMember, pmem)

    if pmem.org == org.pk and g.user.email == pmem.email:
        if OrganizationMember.objects.get_or_create(
                user=g.user.pk,
                org=org.pk,
            )[1]:
            
            flash("You have been added to '%s'" % org.name)
        pmem.delete()
        
    return redirect(url_for('list_snippets', org=org.pk))

@app.route('/<org>/invite', methods=['POST', 'GET'])
@login_required
@can_admin_org
def invite_members(org):
    org = get_object_or_404(Organization, org)
    
    form = InviteUserForm()
    if form.validate_on_submit():
        for email in form.email_list.data.split('\n'):
            email = email.strip()

            pmem = PendingMember.objects.get_or_create(
                email=email,
                org=org.pk,
                defaults={
                    'created_by': g.user.pk,
                }
            )[0]
            
            sig = pmem.get_signature()

            body = render_template('organizations/mail/invite.txt', **{
                'confirm_url': url_for('invite_confirm', org=org.pk, pmem=pmem.pk, sig=sig, _external=True),
                'org': org,
            })
        
            msg = Message("Codebox Organization Invite",
                          recipients=[email],
                          body=body)
            mail.send(msg)
        
        flash("Your invitation(s) have been sent.")
        return redirect(url_for('invite_members', org=org.pk))

    return render_template('organizations/invite_members.html', **{
        'org': org,
        'form': form,
    })
    return redirect('/')

@app.route('/stats')
def stats():
    num_orgs = Organization.objects.count()
    num_users = User.objects.count()
    num_snippets = Snippet.objects.count()
    
    return render_template('organizations/stats.html', **{
        'num_orgs': num_orgs,
        'num_snippets': num_snippets,
        'num_users': num_users,
    })
