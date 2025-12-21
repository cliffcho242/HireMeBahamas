from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).parent / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

spec = spec_from_file_location("boot_app", BACKEND_ROOT / "app.py")
if spec is None or spec.loader is None:
    raise ImportError("Unable to load backend/app.py")

boot_app = module_from_spec(spec)
spec.loader.exec_module(boot_app)


def test_health_route_registered_for_get_and_head():
    matching_routes = [
        route for route in boot_app.app.routes if getattr(route, "path", None) == "/health"
    ]
    assert matching_routes, "Expected /health route to be registered"

    methods = set().union(*[getattr(route, "methods", set()) for route in matching_routes])
    assert "GET" in methods
    assert "HEAD" in methods


def test_health_function_returns_plain_text_ok():
    response = boot_app.health()
    assert response.status_code == 200
    assert response.body == b"ok"
