import uuid
from datetime import datetime
from typing import Optional, Generic, TypeVar, Any

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


# Pydantic Models
ResponseDataType = TypeVar("ResponseDataType")


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        alias_generator=to_camel,
        json_encoders={uuid.UUID: lambda o: str(o)},
    )


class BaseResponse(CustomBaseModel, Generic[ResponseDataType]):
    message: str
    data: Optional[ResponseDataType] = None


class SuccessResponse(BaseResponse, Generic[ResponseDataType]):
    message: str = "Ok"


GenericSuccessResponse = BaseResponse[dict](data={}, message="success")
GenericFailureResponse = BaseResponse[dict](data={}, message="error")


class CustomHttpException(HTTPException):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Internal Server Error"

    def __init__(self, status_code=None, detail=None, **kwargs: dict[str, Any]) -> None:
        super().__init__(
            status_code=status_code or self.STATUS_CODE,
            detail=detail or self.DETAIL,
            **kwargs
        )
