from typing import Generic, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")

class ResponseBase(GenericModel, Generic[T]):
    resultCode: str = "SUCCESS"
    message: str = "Success"
    error_code: Optional[str] = None
    detail: Optional[Dict[str, Any]] = None
    data: Optional[T] = None

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def error(cls, error_code: str, message: str, detail: Optional[Dict[str, Any]] = None):
        return cls(
            resultCode="FAILURE",
            message=message,
            error_code=error_code,
            detail=detail
        )

    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "Success"):
        return cls(
            resultCode="SUCCESS",
            message=message,
            data=data
        )