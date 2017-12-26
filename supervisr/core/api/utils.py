"""
Supervisr Core API Utils
"""

from django.http import HttpResponse, JsonResponse
from datetime import date, datetime
from datetime import timezone


def api_response(req, data):
    """Prase data in correct format extracted from request"""
    selected_format = 'json'
    # Check if format is set as a GET Param
    format_keys = ['type', 'format']
    for key in format_keys:
        if key in req.GET:
            selected_format = req.GET.get(key)

    _globals = globals()
    handler_name = 'api_response_%s' % selected_format
    if not isinstance(data, dict) or 'data' not in data:
        data = {'data': data}
    code = data.get('code', 200)
    handler = _globals.get(handler_name, None)
    if handler is not None:
        return handler(data=data, code=code)
    return JsonResponse({'error': "type '%s' not found" % selected_format, 'code': 400}, status=400)

def api_response_openid(code, data):
    """This method only renames some keys for OpenID, then uses JSON"""
    remap_table = {
        'id': 'sub',
        'pk': 'sub',
        'first_name': 'name',
        'username': 'preferred_username',
        'email': 'email',
    }
    new_data = {}
    for init_key, dest_key in remap_table.items():
        if init_key in data['data']:
            new_data[dest_key] = data['data'][init_key]
    return api_response_json(code, new_data)

def api_response_json(code, data):
    """Pass dict to django and let it handle the encoding etc"""
    import json
    def date_helper(obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, date):
            obj = datetime.combine(obj, datetime.min.time())
        if isinstance(obj, datetime):
            return obj.replace(tzinfo=timezone.utc).timestamp()

        raise TypeError ("Type %s not serializable" % type(obj))

    data = json.dumps(data, sort_keys=True, indent=4, default=date_helper)
    return HttpResponse(data, content_type='application/json', status=code)

def api_response_yaml(code, data):
    """Return data as yaml dict"""
    import yaml
    return HttpResponse(yaml.dump(data, default_flow_style=False),
                        content_type='text/x-yaml', status=code)
