from fastapi import APIRouter

router = APIRouter()

@router.get("/health/ping")
def ping():
    """Ultra-fast health ping endpoint.
    
    ✅ PRODUCTION-GRADE: Database-free, instant response.
    Returns immediately without database check.
    Use this for load balancer health checks and quick availability tests.
    
    ❌ No DB access
    ❌ No external calls
    ❌ No disk access
    Target latency: < 30ms
    """
    return {"status": "ok"}
