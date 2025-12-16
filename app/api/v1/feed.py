from fastapi import APIRouter

router = APIRouter(
    prefix="/feed",
    tags=["Feed"],
)

@router.get("/")
def get_feed():
    return {"feed": []}
