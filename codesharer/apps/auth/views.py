from flask import current_app as app, g, request, Module, render_template, redirect, url_for

from codesharer.apps.snippets.models import Snippets
from codesharer.apps.snippets.forms import NewSnippetForm

frontend = Module(__name__)

@frontend.route('/verify')
def verify_start():
    return render_template('snippets/verify.html', **{})

@frontend.route('/verify/confirm', methods=['GET', 'POST'])
def verify_complete():
    """
    Creates a new snippet for an organization.
    """

    snippets = Snippets(g.redis)

    form = NewSnippetForm()
    if form.validate_on_submit():
        # Generate a unique slug from name
        snippet = snippets.new(text=form.text.data)

        flash("Success")

        return redirect(url_for('snippet_details', org=org, id=snippet.id))

    return render_template('snippets/new_snippet.html', **{
        'org': org,
    })
