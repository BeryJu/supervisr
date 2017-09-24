"""
Supervisr Core API Utils
"""

import os

from django.http import HttpResponse, JsonResponse


def api_response(req, data):
    """
    Prase data in correct format extracted from request
    """
    selected_format = 'json'
    # Check if it is set as file extension
    ext_format = os.path.splitext(req.path)[1][1:]
    if ext_format != '':
        selected_format = ext_format

    _globals = globals()
    handler_name = 'api_response_%s' % selected_format
    handler = _globals[handler_name] if handler_name in _globals else None
    if handler is not None:
        return handler(data)
    return JsonResponse({'error': "type '%s' not found" % selected_format})

def api_response_openid(data):
    """
    This method only renames some keys for OpenID, then uses JSON
    """
    remap_table = {
        'id': 'sub',
        'pk': 'sub',
        'first_name': 'name',
        'username': 'preferred_username',
    }
    for init_key, dest_key in remap_table.items():
        if init_key in data:
            data[dest_key] = data[init_key]
            del data[init_key]
    return api_response_json(data)

def api_response_json(data):
    """
    Pass dict to django and let it handle the encoding etc
    """
    import json
    data = json.dumps(data, sort_keys=True, indent=4)
    return HttpResponse(data, content_type='application/json')

def api_response_yaml(data):
    """
    Return data as yaml dict
    """
    import yaml
    return HttpResponse(yaml.dump(data, default_flow_style=False),
                        content_type='text/x-yaml')