from fastapi import APIRouter

router = APIRouter(
    prefix="/debug",
    tags=["Debug"],
)

@router.get("/")
def get_debug():
    return {"debug": []}
