from pydantic import BaseModel, ConfigDict
from typing import TypeVar, Generic, Optional, Any

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = ""
    data: Optional[T] = None
    errors: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)
