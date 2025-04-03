from typing import Any, Optional

from pydantic import BaseModel, UUID4


class ElementDimensions(BaseModel):
    left: int = 0
    top: int = 0
    width: int = 0
    height: int = 0


class BrowserElement(BaseModel):
    text: str = ""
    tag_name: str = ""
    id: str = ""
    class_name: str = ""
    href: str = ""
    src: str = ""
    alt: str = ""
    title: str = ""
    type: str = ""
    name: str = ""
    placeholder: str = ""
    role: str = ""
    dimensions: ElementDimensions = ElementDimensions()


class InteractionStep(BaseModel):
    prompt: str
    step: str
    code_body: str = ""
    _elements: list[BrowserElement] = []


class BrowserSession(BaseModel):
    id: UUID4
    steps: list[InteractionStep]
    user_command: str


class StartSessionRequest(BaseModel):
    command: str
    variables: dict[str, Any] = {}
    model: str = "anthropic"


class GenerateNextStepResponse(BaseModel):
    step: str
    code_body: str
