from flask import request, Module, render_template, \
                  redirect, url_for, abort, g

from codebox.apps.auth.models import User
from codebox.apps.auth.decorators import login_required
from codebox.apps.organizations.decorators import can_view_org
from codebox.apps.organizations.models import Organization
from codebox.apps.snippets.models import Snippet
from codebox.apps.snippets.forms import NewSnippetForm
from codebox.utils.shortcuts import get_object_or_404

frontend = Module(__name__)

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

@frontend.route('/<org>/new', methods=['GET', 'POST'])
@login_required
@can_view_org
def new_snippet(org):
    """
    Creates a new snippet for an organization.
    """
    org = get_object_or_404(Organization, org)

    form = NewSnippetForm(obj=org)
    if form.validate_on_submit():
        # Generate a unique slug from name
        snippet = Snippet.objects.create(
            org=org,
            text=form.text.data,
            lang=form.lang.data,
            user=g.user.pk,
        )

        if request.is_xhr:
            return 'Success'

        return redirect(url_for('snippet_detail', org=org.pk, id=snippet.pk))

    return render_template('snippets/new_snippet.html', **{
        'org': org,
        'form': form,
    })

@frontend.route('/<org>')
@login_required
@can_view_org
def list_snippets(org):
    org = get_object_or_404(Organization, org)
    org_members = org.get_all_members()
    
    snippets = list(Snippet.objects.filter(org=org.pk))
    snippets_users = User.objects.get_many([s.user for s in snippets])

    return render_template('organizations/detail.html', **{
        'org': org,
        'org_members': org_members,
        'snippets': snippets,
        'snippets_users': dict([(u.pk, u) for u in snippets_users]),
        'snippets_orgs': {org.pk: org},
    })

@frontend.route('/<org>/search')
@login_required
@can_view_org
def search_snippets(org):
    query = request.args.get('q')
    
    org = get_object_or_404(Organization, org)
    org_members = org.get_all_members()

    if query:    
        i, n = 0, 0
        results = []
        words = query.lower().split(' ')
        for snippet in Snippet.objects.all():
            i += 1
            text = snippet.text.lower().split(' ')
            for word in words:
                for otherword in text:
                    if word in otherword:
                        results.append(snippet)
                        n += 1
            if i > 1000 or n > 25:
                break
        if results:        
            snippets_users = User.objects.get_many([s.user for s in results])
        else:
            snippets_users = []
    else:
        results = []
        snippets_users = []

    return render_template('organizations/search.html', **{
        'query': query,
        'org': org,
        'org_members': org_members,
        'snippets': results,
        'snippets_users': dict([(u.pk, u) for u in snippets_users]),
    })
