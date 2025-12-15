# Only import the core routers needed by main.py
# Other routers can be imported directly when needed
from . import auth, users, jobs

__all__ = [
    'auth',
    'users',
    'jobs',
]
