from flask import current_app as app, g, request, Module, render_template, redirect
from disqusapi import DisqusAPI

from sherlock.apps.bayes import Bayes
from sherlock.apps.classifier.models import Classifier
from sherlock.utils.readability import summarize_url

frontend = Module(__name__)

@frontend.route('/:org/new', methods=['GET', 'POST'])
def new_snippet(org):
    """
    Creates a new snippet for an organization.
    """

    snippets = Snippets(g.redis)
    
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
