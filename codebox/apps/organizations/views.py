from codebox.apps.auth.decorators import login_required
from flask import g, request, Module, render_template, redirect, url_for, flash

from codebox.apps.organizations.forms import NewOrganizationForm
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

@orgs.route('/verify/<org>')
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
            owned_by=porg.created_by,
        )
        
        OrganizationMember.objects.create(
            org=org.pk,
            user=porg.created_by,
        )
        
        flash("Your organization was created successfully!")
        
        return redirect(url_for('list_snippets', org=org))
    return redirect('/')
