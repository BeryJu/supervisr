"""
Supervisr Core API Utils
"""

from django.http import JsonResponse


def api_response(req, data):
    # Check which format is requested, default to json
    format_keys = ['type', 'format']
    format = 'json'
    for key in format_keys:
        if key in req.GET:
            format = req.GET.get(key)

    _globals = globals()
    handler_name = 'api_response_%s' % format
    handler = _globals[handler_name] if handler_name in _globals else None
    if handler is not None:
        return handler(data)
    else:
        return JsonResponse({'error': 'type "%s" not found' % format})

def api_response_json(data):
    """
    Pass dict to django and let it handle the encoding etc
    """
    return JsonResponse(data)

def api_response_openid(data):
    """
    This method only renames some keys for OpenID, then uses JSON
    """
    remap_table = {
        'id': 'sub',
        'pk': 'sub',
    }
    for init_key, dest_key in remap_table.items():
        if init_key in data:
            data[dest_key] = data[init_key]
            del data[init_key]
    return api_response_json(data)

def api_response_yaml(data):
    return JsonResponse({'error': 'not implemented yet'})
    # TODO: Implement yaml handler
