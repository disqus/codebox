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