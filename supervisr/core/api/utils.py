"""Supervisr Core API Utils"""

from datetime import date, datetime, timezone

from django.http import HttpResponse, JsonResponse


def api_response(request, data, code=200):
    """Parse data in correct format extracted from request"""
    selected_format = 'json'
    # Check if format is set as a GET Param
    format_keys = ['type', 'format']
    for key in format_keys:
        if key in request.GET:
            selected_format = request.GET.get(key)

    _globals = globals()
    handler_name = 'api_response_%s' % selected_format
    if not isinstance(data, dict) or 'data' not in data:
        data = {'data': data, 'code': code}
    elif 'code' not in data:
        data['code'] = code
    handler = _globals.get(handler_name, None)
    if handler is not None:
        return handler(data=data, code=code)
    return JsonResponse({'error': "type '%s' not found" % selected_format, 'code': 400}, status=400)


def api_response_openid(code, data):
    """Serialize data to JSON then apply OpenID field names."""
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
    """Serialize data to JSON"""
    def date_helper(obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, date):
            obj = datetime.combine(obj, datetime.min.time())
        if isinstance(obj, datetime):
            return obj.replace(tzinfo=timezone.utc).timestamp()

        raise TypeError("Type %s not serializable" % type(obj))

    return JsonResponse(data, status=code, json_dumps_params={
        'sort_keys': True,
        'indent': 4,
        'default': date_helper
    })


def api_response_yaml(code, data):
    """Serialize data to YAML"""
    import yaml
    return HttpResponse(yaml.dump(data, default_flow_style=False),
                        content_type='text/x-yaml', status=code)
