from pydantic import BaseModel
from typing import Optional

class DefaultResponse(BaseModel):
    """Стандартный ответ от API."""
    error: bool
    message: Optional[str]
