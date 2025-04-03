from fastapi import APIRouter

from src.core.models import SuccessResponse

from .models import StartSessionRequest, BrowserSession
from .agentic_operator import AgenticBrowserOperator

router = APIRouter()


@router.post(
    path="/start",
    response_model=SuccessResponse[BrowserSession],
    tags=["interact"],
)
async def start_payment_session(request: StartSessionRequest):
    operator = AgenticBrowserOperator(model=request.model)
    session = await operator.start_session(request.command, request.variables)
    return SuccessResponse[BrowserSession](data=session)
