from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.core.models import CustomHttpException
from src.interact.router import router as interact_router

app = FastAPI()

app.include_router(router=interact_router, prefix="/interact", tags=["interact"])

app.add_exception_handler(
    exc_class_or_status_code=CustomHttpException,
    handler=lambda r, e: JSONResponse(
        status_code=e.status_code,
        content={"message": "Error", "data": {"error": e.detail}},
    ),
)
app.add_exception_handler(
    exc_class_or_status_code=Exception,
    handler=lambda r, e: JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Error", "data": {"error": "Internal Server Error"}},
    ),
)
