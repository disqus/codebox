from flask import current_app as app, g, request, Module, flash, render_template, \
                  redirect, url_for

from codesharer.apps.auth.decorators import login_required
from codesharer.apps.snippets.models import Snippet
from codesharer.apps.snippets.forms import NewSnippetForm

frontend = Module(__name__)

@frontend.route('/')
@login_required
def dashboard():
    """
    Shows organizations/recent pastes/etc
    """

    return render_template('snippets/dashboard.html', **{

    })

@frontend.route('/<org>/new', methods=['GET', 'POST'])
@login_required
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
            author=request.user.id,
        )

        if request.is_xhr:
            return 'Success'

        flash("Success")

        return redirect(url_for('snippet_details', org=org, id=snippet.id))

    return render_template('snippets/new_snippet.html', **{
        'org': org,
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
