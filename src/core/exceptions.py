from typing import Any

from fastapi import HTTPException, status


class CustomHttpException(HTTPException):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Internal Server Error"

    def __init__(self, status_code=None, detail=None, **kwargs: dict[str, Any]) -> None:
        super().__init__(
            status_code=status_code or self.STATUS_CODE,
            detail=detail or self.DETAIL,
            **kwargs
        )


class NotFound(CustomHttpException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DETAIL = "Resource not found"


class BadRequest(CustomHttpException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    DETAIL = "Bad Request"
