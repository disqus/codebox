from flask import request, Blueprint, render_template, abort, g

from codebox.apps.auth.models import User
from codebox.apps.auth.decorators import login_required
from codebox.apps.organizations.decorators import can_view_org
from codebox.apps.organizations.models import Organization
from codebox.apps.snippets.models import Snippet
from codebox.utils.shortcuts import get_object_or_404

frontend = Blueprint('snippets', __name__)

@frontend.route('/')
@login_required
def dashboard():
    """
    Shows organizations/recent pastes/etc
    """

    snippets = list(Snippet.objects.filter(dashboard=g.user.pk))
    snippets_users = User.objects.get_many([s.user for s in snippets])
    snippets_orgs = Organization.objects.get_many([s.org for s in snippets])
    
    return render_template('snippets/dashboard.html', **{
        'snippets': snippets,
        'snippets_users': dict([(u.pk, u) for u in snippets_users]),
        'snippets_orgs': dict([(u.pk, u) for u in snippets_orgs])
    })

@frontend.route('/search')
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

@frontend.route('/<org>/view/<id>')
@login_required
@can_view_org
def snippet_detail(org, id):
    org = get_object_or_404(Organization, org)

    snippet = get_object_or_404(Snippet, id)
    if snippet.org != org.pk:
        abort(404)

    user = User.objects.get(snippet.user)
        
    return render_template('snippets/detail.html', **{
        'snippet': snippet,
        'org': org,
        'user': user,
    })