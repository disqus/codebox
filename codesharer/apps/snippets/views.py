from flask import request, Module, flash, render_template, \
                  redirect, url_for

from codesharer.apps.auth.decorators import login_required
from codesharer.apps.organizations.models import Organization
from codesharer.apps.snippets.models import Snippet
from codesharer.apps.snippets.forms import NewSnippetForm

frontend = Module(__name__)

@frontend.route('/')
#@login_required
def dashboard():
    """
    Shows organizations/recent pastes/etc
    """

    snippets = list(Snippet.objects.all())[:10]

    return render_template('snippets/dashboard.html', **{
            'snippets': snippets,
            })

@frontend.route('/<org>')
#@login_required
def org_detail(org):
    org = Organization.objects.get(org)

    return render_template('organizations/detail.html', **{
            'org': org,
            })

@frontend.route('/<org>/view/<id>')
#@login_required
def snippet_detail(org, id):
    snippet = Snippet.objects.get(id)

    return render_template('snippets/detail.html', **{
            'snippet': snippet,
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
            user=request.user.id,
        )

        if request.is_xhr:
            return 'Success'

        flash("Success")

        return redirect(url_for('snippet_details', org=org, id=snippet.id))

    return render_template('snippets/new_snippet.html', **{
        'org': org,
        'form': form,
    })

@frontend.route('/<org>')
@login_required
def list_snippets(org):
    """
    Displays a list of all snippets for an organization
    """

    snippets = Snippet.objects.all()

    return render_template('snippets/list_snippets.html', **{
        'snippet_list': snippets[:10],
    })
