from flask import current_app as app, g, request, Module, render_template, redirect, url_for

from codesharer.apps.snippets.models import Snippets
from codesharer.apps.snippets.forms import NewSnippetForm

frontend = Module(__name__)

@frontend.route('/verify')
def verify_app():
    return render_template('snippets/verify.html', **{})
