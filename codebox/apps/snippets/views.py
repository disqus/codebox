from flask import request, render_template, abort, g, redirect, \
                  url_for

from codebox import app
from codebox.apps.auth.models import User
from codebox.apps.auth.decorators import login_required
from codebox.apps.organizations.decorators import can_view_org
from codebox.apps.organizations.models import Organization
from codebox.apps.snippets.forms import EditSnippetForm, NewSnippetForm
from codebox.apps.snippets.models import Snippet
from codebox.utils.shortcuts import get_object_or_404

@app.route('/')
@login_required
def dashboard():
    """
    Shows organizations/recent pastes/etc
    """

    snippets = list(Snippet.objects.filter(dashboard=g.user.pk))
    for s in snippets:
        if not s.text:
            Snippet.objects.remove_from_index(s.pk, dashboard=g.user.pk)
    snippets_users = User.objects.get_many([s.user for s in snippets])
    snippets_orgs = Organization.objects.get_many([s.org for s in snippets])

    my_orgs = g.user.get_all_organizations()
    
    if len(my_orgs) == 1:
        return redirect(url_for('list_snippets', org=my_orgs[0].pk))
    
    return render_template('snippets/dashboard.html', **{
        'snippets': snippets,
        'snippets_users': dict([(u.pk, u) for u in snippets_users]),
        'snippets_orgs': dict([(u.pk, u) for u in snippets_orgs])
    })

@app.route('/search')
@login_required
def search_snippets():
    query = request.args.get('q')
    
    if query:    
        i, n = 0, 0
        results = set()
        words = query.lower().split(' ')
        for snippet in Snippet.objects.filter(dashboard=g.user.pk):
            i += 1
            tokens = snippet.text.lower().split(' ')
            if snippet.keywords:
                tokens.extend(snippet.keywords.lower().split(' '))
            for word in words:
                for otherword in tokens:
                    if word in otherword:
                        results.add(snippet)
                        n += 1
            if i > 1000 or n > 25:
                break
    else:
        results = []

    if results:
        snippets_users = User.objects.get_many([s.user for s in results])
        snippets_orgs = Organization.objects.get_many([s.org for s in results])
    else:
        snippets_users = []
        snippets_orgs = []

    return render_template('snippets/search.html', **{
        'query': query,
        'snippets': results,
        'snippets_users': dict([(u.pk, u) for u in snippets_users]),
        'snippets_orgs': dict([(u.pk, u) for u in snippets_orgs])
    })

@app.route('/<org>/<uuid:id>')
@login_required
@can_view_org
def snippet_detail(org, id):
    org = get_object_or_404(Organization, org)

    snippet = get_object_or_404(Snippet, id)
    if snippet.org != org.pk:
        abort(404)

    user = User.objects.get(snippet.user)
        
    return render_template('snippets/details.html', **{
        'snippet': snippet,
        'org': org,
        'user': user,
    })

@app.route('/<org>/<uuid:id>/edit', methods=['GET', 'POST'])
@login_required
@can_view_org
def edit_snippet(org, id):
    """
    Creates a new snippet for an organization.
    """
    org = get_object_or_404(Organization, org)

    snippet = get_object_or_404(Snippet, id)
    if snippet.org != org.pk:
        abort(404)

    user = User.objects.get(snippet.user)
    if snippet.user != user.pk:
        abort(404)

    form = EditSnippetForm(obj=org, lang=snippet.lang, text=snippet.text, keywords=snippet.keywords)
    if form.validate_on_submit():
        # Generate a unique slug from name
        snippet.text = form.text.data
        snippet.lang = form.lang.data
        snippet.keywords = form.keywords.data

        return redirect(url_for('snippet_detail', org=org.pk, id=snippet.pk))

    return render_template('snippets/edit.html', **{
        'org': org,
        'snippet': snippet,
        'form': form,
    })

@app.route('/<org>/new', methods=['GET', 'POST'])
@login_required
@can_view_org
def new_snippet(org):
    """
    Edits a snippet.
    """
    org = get_object_or_404(Organization, org)

    form = NewSnippetForm(obj=org, csrf_enabled=(not g.is_api))
    if form.validate_on_submit():
        # Generate a unique slug from name
        snippet = Snippet.objects.create(
            org=org,
            text=form.text.data,
            lang=form.lang.data,
            keywords=form.keywords.data,
            user=g.user.pk,
        )

        return redirect(url_for('snippet_detail', org=org.pk, id=snippet.pk))

    return render_template('snippets/new.html', **{
        'org': org,
        'form': form,
    })

@app.route('/<org>/<uuid:id>/delete', methods=['GET', 'POST'])
@login_required
@can_view_org
def delete_snippet(org, id):
    """
    Deletes a new snippet.
    """
    org = get_object_or_404(Organization, org)

    snippet = get_object_or_404(Snippet, id)
    if snippet.org != org.pk:
        abort(404)

    user = User.objects.get(snippet.user)
    if snippet.user != user.pk:
        abort(404)

    if request.form.get('confirm'):
        snippet.delete()

        return redirect(url_for('list_snippets', org=org.pk))

    return render_template('snippets/delete.html', **{
        'org': org,
        'snippet': snippet,
    })

@app.route('/<org>')
@login_required
@can_view_org
def list_snippets(org):
    org = get_object_or_404(Organization, org)
    
    snippets = list(Snippet.objects.filter(org=org.pk))
    for s in snippets:
        if not s.text:
            Snippet.objects.remove_from_index(s.pk, org=org.pk)
    snippets_users = User.objects.get_many([s.user for s in snippets])

    return render_template('snippets/list.html', **{
        'org': org,
        'snippets': snippets,
        'snippets_users': dict([(u.pk, u) for u in snippets_users]),
        'snippets_orgs': {org.pk: org},
    })

