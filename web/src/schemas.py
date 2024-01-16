from pydantic import BaseModel

class DefaultResponse(BaseModel):
    """Стандартный ответ от API."""
    error: bool
    message: Optional[str]
