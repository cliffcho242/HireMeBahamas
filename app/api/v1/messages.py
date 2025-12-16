from fastapi import APIRouter

router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
)

@router.get("/")
def get_messages():
    return {"messages": []}
