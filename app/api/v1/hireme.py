from fastapi import APIRouter

router = APIRouter(
    prefix="/hireme",
    tags=["HireMe"],
)

@router.get("/")
def get_hireme():
    return {"hireme": []}
