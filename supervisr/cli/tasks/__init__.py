"""supervisr invoke tasks"""

def _import_submodules(package_name):
    """Import all submodules of a module, recursively

    :param package_name: Package name
    :type package_name: str
    :rtype: dict[types.ModuleType]
    """
    import os
    import sys
    import pkgutil
    import importlib
    package = sys.modules[package_name]
    modules = {
        name: importlib.import_module(package_name + '.' + name)
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__)
    }
    if os.getenv('SUPERVISR_PACKAGED', "False").title() == 'True':
        del modules['env']
        del modules['build']
        del modules['internal']
    return modules


__all__ = _import_submodules(__name__).keys()
