from flask import current_app as app, g, request, Module, render_template, redirect
from disqusapi import DisqusAPI

from sherlock.apps.snippets.models import Snippets
from sherlock.apps.snippets.forms import NewSnippetForm
from sherlock.utils.readability import summarize_url

frontend = Module(__name__)

@frontend.route('/:org/new', methods=['GET', 'POST'])
def new_snippet(org):
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

@frontend.route('/:org', methods=['GET', 'POST'])
def list_snippets(org):
    """
    Displays a list of all snippets for an organization
    """
    
    snippets = Snippets(g.redis)
    
    return render_template('snippets/list_snippets.html', **{
        'snippet_list': snippet_list[:10],
    })
