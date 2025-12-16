from fastapi import APIRouter

router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)

@router.get("/")
def get_upload():
    return {"upload": []}
