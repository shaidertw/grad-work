from fastapi import APIRouter

from src.schemas import DefaultResponse

router = APIRouter(
    prefix="/api",
)

@router.get("")
def default() -> DefaultResponse:
    return DefaultResponse(error=False, message="OK")
