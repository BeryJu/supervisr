"""Supervisr Core CRUD API"""

from supervisr.core.api.base import API


class CRUDAPI(API):
    """Basic API for Models"""

    ALLOWED_VERBS = {
        'GET': ['read'],
        'POST': ['create', 'update', 'delete'],
    }

    def create(self, request, data):
        """Create instance based on request data"""
        raise NotImplementedError()

    def read(self, request, data):
        """Show list of models"""
        raise NotImplementedError()

    def update(self, request, data):
        """Update model based on pk parameter"""
        raise NotImplementedError()

    def delete(self, request, data):
        """Delete model instance"""
        raise NotImplementedError()
