"""supervisr dns api responses"""

from django.http import HttpResponse


class BadAuthResponse(HttpResponse):
    """bad auth Response"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = 'bad auth'


class GoodResponse(HttpResponse):
    """good Response"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = 'good'
