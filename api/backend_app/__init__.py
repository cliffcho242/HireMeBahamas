"""
Backend application package.

This package contains all backend modules and must properly expose submodules
for module aliasing to work (e.g., when backend_app is aliased as 'app').
"""

# Import and expose core submodule to ensure it's accessible via aliasing
from . import core

__all__ = ['core']
