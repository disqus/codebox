"""
codebox.utils.shortcuts
~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from flask import abort

def get_object_or_404(model, pk):
    try:
        return model.objects.get(pk)
    except model.DoesNotExist:
        return abort(404)

def get_object_or_none(model, pk):
    try:
        return model.objects.get(pk)
    except model.DoesNotExist:
        return None