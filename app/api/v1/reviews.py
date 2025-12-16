from fastapi import APIRouter

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
)

@router.get("/")
def get_reviews():
    return {"reviews": []}
