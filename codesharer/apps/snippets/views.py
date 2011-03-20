from flask import request, Module, flash, render_template, \
                  redirect, url_for, abort

from codesharer.apps.auth.decorators import login_required
from codesharer.apps.organizations.decorators import can_view_org
from codesharer.apps.organizations.models import Organization
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

    return render_template('snippets/dashboard.html', **{
            'snippets': snippets,
            })

@frontend.route('/<org>/view/<id>')
#@login_required
#@can_view_org
def snippet_detail(org, id):
    snippet = get_object_or_404(Snippet, id)
    if snippet.org != org:
        abort(404)
        
    return render_template('snippets/detail.html', **{
            'snippet': Snippet.objects.get(id)
            })

@frontend.route('/<org>/new', methods=['GET', 'POST'])
#@login_required
def new_snippet(org):
    """
    Creates a new snippet for an organization.
    """

    snippets = Snippet.objects.all()

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
@login_required
@can_view_org
def list_snippets(org):
    org = get_object_or_404(Organization, org)
    
    snippets = list(Snippet.objects.for_index('org', org, 0, 10))

    return render_template('organizations/detail.html', **{
            'org': org,
            'snippets': snippets,
            })
