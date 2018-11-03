"""supervisr core graph views"""
from typing import List, Union

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ManyToManyField, Model, Q
from django.http import Http404, HttpRequest, HttpResponse
from django.views.generic import View
from graphviz import Digraph

from supervisr.core.models import (CastableModel, ProviderInstance, User,
                                   UserAcquirable)
from supervisr.core.utils import class_to_path


class GraphView(LoginRequiredMixin, View):
    """View to generate Graph for a model instance"""

    __graph = None
    model = None
    exclude_models = [ProviderInstance, User]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__graph = Digraph('G')

        self.__graph.attr('node', shape='record')
        self.__graph.attr(rankdir='LR')
        self.__graph.format = 'svg'
        if self.model is None:
            raise ValueError("`self.model` must be overwritten.")

    def get_label(self, model: Model) -> str:
        """Get label for model"""
        return "%s | %s" % (class_to_path(model.__class__), str(model))

    def get_unique(self, model: Model) -> str:
        """Get unique Model identifier"""
        return "%s#%s" % (class_to_path(model.__class__), model.pk)

    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        """Walk through model subfields and render SVG"""
        query = Q(**kwargs)
        if issubclass(self.model, UserAcquirable):
            query &= Q(users__in=[request.user])
        root_instance = self.model.objects.filter(query).first()
        if not root_instance:
            raise Http404
        self.walk(root_instance)
        return HttpResponse(self.__graph.pipe().decode('utf-8'), content_type='image/svg+xml')

    def __get_walkable_field_names(self, model: Model) -> List[str]:
        """Get a list with names of all fields that can be walked"""
        fields_to_walk = []
        fields = getattr(model, '_meta').get_fields()
        for field in fields:
            if isinstance(field, ManyToManyField):
                fields_to_walk.append(field.name)
        return fields_to_walk

    def walk(self, root: Model, parent_name: Union[str, None] = None):
        """Walk through root, adding it itself and setting up edges"""
        # Check if model instance should be excluded
        if root.__class__ in self.exclude_models:
            return
        if isinstance(root, CastableModel):
            root = root.cast()
        label = self.get_label(root)
        root_uniq = self.get_unique(root)
        # Add root node
        self.__graph.node(name=root_uniq, label=label)
        if parent_name:
            self.__graph.edge(tail_name=parent_name, head_name=root_uniq)
        # Check if model instance requires further walking
        for field_name in self.__get_walkable_field_names(root):
            for field_rel in getattr(root, field_name).all():
                self.walk(field_rel, root_uniq)
