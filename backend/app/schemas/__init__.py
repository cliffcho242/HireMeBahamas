"""
Schemas package initialization with Pydantic forward reference fix.

This module injects typing exports into schema modules to fix Pydantic's
forward reference resolution issues.
"""
import importlib
from typing import Optional, List, Dict, Union, Any


def inject_typing_exports(module):
    """Inject typing module exports into a module's namespace.
    
    This is required for Pydantic to properly evaluate forward references.
    When Pydantic evaluates forward references, it looks in the module's 
    __dict__ for type names like Optional, List, etc.
    
    Args:
        module: The module object to inject typing exports into
    """
    module.__dict__['Optional'] = Optional
    module.__dict__['List'] = List
    module.__dict__['Dict'] = Dict
    module.__dict__['Union'] = Union
    module.__dict__['Any'] = Any


# Inject typing exports into this module
inject_typing_exports(__import__(__name__))

# Inject typing exports into all schema submodules
_schema_modules = ['auth', 'job', 'message', 'post', 'review']
for _module_name in _schema_modules:
    try:
        _module = importlib.import_module(f'.{_module_name}', package='app.schemas')
        inject_typing_exports(_module)
    except ImportError:
        # Skip modules that might not be available (graceful degradation)
        pass
