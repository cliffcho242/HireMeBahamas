from fastapi import APIRouter

router = APIRouter(
    prefix="/profile_pictures",
    tags=["Profile Pictures"],
)

@router.get("/")
def get_profile_pictures():
    return {"profile_pictures": []}
