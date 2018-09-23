"""supervisr core model utils"""
from typing import Iterable, List

from django.db.models import ManyToManyField, ManyToOneRel, Model

from supervisr.core.decorators import time
from supervisr.core.models import CastableModel


@time('supervisr.core.utils.models.walk_m2m')
def walk_m2m(root: Model,
             exclude_classes: Iterable[Model] = None,
             only_classes: Iterable[Model] = None,
             prevent_duplicates: bool = True) -> List[Model]:
    """Walk through all m2m fields and collect all instances.

    Args:
        root (Model): Root Model instance which will be walked
        exclude_classes (Iterable[Model], optional): Defaults to None. List of classes to ignore.
        only_classes (Iterable[Model], optional): Defaults to None. List of to add.
        prevent_duplicates (bool): Prevent duplicates from being listed multiple times.
            If this is disabled, infinite loops can occur.

    Returns:
        List[Model]: Flat list of all found Model instances
    """
    if exclude_classes is None:
        exclude_classes = []
    if only_classes is None:
        only_classes = []
    models = []
    all_model_list = []

    def get_walkable_field_names(model: Model) -> List[str]:
        """Get a list with names of all fields that can be walked"""
        fields_to_walk = []
        fields = getattr(model, '_meta').get_fields()
        for field in fields:
            if isinstance(field, (ManyToManyField, ManyToOneRel)):
                fields_to_walk.append(field.name)
        return fields_to_walk

    def walk(root: Model):
        """Walk through root, adding it itself and setting up edges"""
        if isinstance(root, CastableModel):
            root = root.cast()
        if prevent_duplicates and root in all_model_list:
            return
        # Check if model instance should be excluded or included
        if (exclude_classes and root.__class__ not in exclude_classes) or \
                (only_classes and root.__class__ in only_classes) or \
                (only_classes == exclude_classes == []):
            models.append(root)
        # Also add if subclass of only_classes
        if any([issubclass(root.__class__, x) for x in only_classes]):
            models.append(root)
        # Keep a second list with all models so we can check for duplicates,
        # even if class would normally be filtered out
        all_model_list.append(root)
        # Check if model instance requires further walking
        for field_name in get_walkable_field_names(root):
            field = getattr(root, field_name, getattr(root, field_name + '_set', None))
            if field:
                for field_rel in field.all():
                    walk(field_rel)

    walk(root)
    return models
