from flask import request, Module, flash, render_template, \
                  redirect, url_for, abort

from codesharer.apps.auth.models import User
from codesharer.apps.auth.decorators import login_required
from codesharer.apps.organizations.decorators import can_view_org
from codesharer.apps.organizations.models import Organization, OrganizationMember
from codesharer.apps.snippets.models import Snippet
from codesharer.apps.snippets.forms import NewSnippetForm
from codesharer.utils.shortcuts import get_object_or_404

frontend = Module(__name__)

@frontend.route('/')
#@login_required
def dashboard():
    """
    Shows organizations/recent pastes/etc
    """

    snippets = list(Snippet.objects.all(0, 10))

    user = User.objects.get(1)
    my_organizations = user.get_all_organizations(1)

    return render_template('snippets/dashboard.html', **{
            'snippets': snippets,
            'my_organizations': my_organizations,
            })

@frontend.route('/<org>/view/<id>')
#@login_required
#@can_view_org
def snippet_detail(org, id):
    org = get_object_or_404(Organization, org)

    snippet = get_object_or_404(Snippet, id)
    if snippet.org != org.pk:
        abort(404)
    
    return render_template('snippets/detail.html', **{
            'snippet': snippet,
            'org': org,
            })

@frontend.route('/<org>/new', methods=['GET', 'POST'])
#@login_required
def new_snippet(org):
    """
    Creates a new snippet for an organization.
    """
    org = get_object_or_404(Organization, org)

    form = NewSnippetForm()
    if form.validate_on_submit():
        # Generate a unique slug from name
        snippet = Snippet.objects.create(
            org=org,
            text=form.text.data,
            lang=1,
            user=1,
        )

        if request.is_xhr:
            return 'Success'

        flash("Success")

        return redirect(url_for('snippet_detail', org=org, id=snippet.pk))

    return render_template('snippets/new_snippet.html', **{
        'org': org,
        'form': form,
    })

@frontend.route('/<org>')
# @login_required
# @can_view_org
def list_snippets(org):
    org = get_object_or_404(Organization, org)
    org_members = org.get_all_members()
    
    snippets = list(Snippet.objects.for_index('org', org.pk, 0, 10))

    return render_template('organizations/detail.html', **{
            'org': org,
            'org_members': org_members,
            'snippets': snippets,
            })
