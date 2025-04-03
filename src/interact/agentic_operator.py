import uuid
import json
import traceback
import asyncio
from typing import Optional, Tuple, Any

from playwright.async_api import (
    async_playwright,
    Playwright,
    Browser,
    BrowserContext,
)

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import HumanMessagePromptTemplate

from .models import (
    BrowserSession,
    InteractionStep,
    BrowserElement,
    GenerateNextStepResponse,
)
from .config import settings
from .operator import BrowserOperator
from .prompts import (
    GENERATE_NEXT_STEP_SYSTEM_PROMPT,
    GENERATE_NEXT_STEP_HUMAN_PROMPT,
)


class AgenticBrowserOperator(BrowserOperator):
    def __init__(self, model: str = "anthropic"):
        self._initialized: bool = False
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.llm: Optional[ChatOpenAI | ChatAnthropic] = None

        if model == "openai":
            self.llm: ChatOpenAI = ChatOpenAI(
                temperature=0,
                model_name="gpt-4o",
                openai_api_key=settings.OPENAI_API_KEY,
            )
        else:
            self.llm: ChatAnthropic = ChatAnthropic(
                temperature=0,
                model_name="claude-3-7-sonnet-20250219",
                api_key=settings.ANTHROPIC_API_KEY,
                timeout=None,
            )

    async def initialize(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=["--incognito", "--start-maximized"]
        )
        self.context = await self.browser.new_context()
        self._initialized = True

    def _format_code(self, code: str) -> str:
        if "```python" in code and "```" in code.split("```python", 1)[1]:
            code = code.split("```python", 1)[1].split("```", 1)[0].strip()
        elif "```" in code:
            code = code.split("```", 1)[1].split("```", 1)[0].strip()
        return code

    def _format_prompt(
        self,
        command: str,
        previous_steps: list[InteractionStep],
        variables: list[str],
        elements: list[BrowserElement],
        previous_attempt: str = "",
        traceback: str = "",
    ) -> str:
        previous_steps_prompt = "\n".join(
            f"{i + 1}. {ps.step}" for i, ps in enumerate(previous_steps)
        )
        formatted_prompt = GENERATE_NEXT_STEP_HUMAN_PROMPT.format(
            user_command=command,
            previous_steps=previous_steps_prompt,
            variables=variables,
            elements=f"""
            ```json
            {json.dumps(
                [
                    element.model_dump(exclude_defaults=True, exclude={"dimensions"})
                    for element in elements
                ],
            )}
            ```""",
            previous_attempt=previous_attempt,
            traceback=traceback,
        ).content
        return formatted_prompt

    async def generate_next_step(
        self,
        command: str,
        previous_steps: list[InteractionStep],
        variables: list[str],
        elements: list[BrowserElement],
        previous_attempt: str = "",
        traceback: str = "",
    ) -> InteractionStep:
        print(f"Generating step {len(previous_steps) + 1}")

        parser = PydanticOutputParser(pydantic_object=GenerateNextStepResponse)
        prompt_input = f"""{self._format_prompt(
            command, previous_steps, variables, elements, previous_attempt, traceback
        )}\n\n{parser.get_format_instructions()}"""

        template = ChatPromptTemplate.from_messages(
            [
                GENERATE_NEXT_STEP_SYSTEM_PROMPT,
                HumanMessagePromptTemplate.from_template("{prompt_input}"),
            ]
        )
        chain = template | self.llm | parser
        result = await chain.ainvoke({"prompt_input": prompt_input})

        code_body = self._format_code(result.code_body)

        print(f"Step {len(previous_steps) + 1}: {result.step}")
        # print(f"Code:\n{code_body}")

        return InteractionStep(
            prompt=prompt_input,
            step=result.step,
            code_body=code_body,
            _elements=[],
        )

    async def _retry_step(
        self,
        page,
        command: str,
        steps: list[InteractionStep],
        variables: dict[str, Any],
        previous_attempt: str,
        error: str,
    ) -> Tuple[bool, str, InteractionStep, bool]:
        elements = await self.detect_interactive_elements(page)
        current_step = await self.generate_next_step(
            command,
            steps,
            list(variables.keys()),
            elements,
            previous_attempt=previous_attempt,
            traceback=error,
        )
        success, error, is_last_step = await self.execute_code(
            page, current_step.code_body, variables
        )
        return success, error, current_step, is_last_step

    async def start_session(
        self, command: str, variables: dict[str, Any]
    ) -> BrowserSession:
        if not self._initialized:
            await self.initialize()

        if not command:
            raise Exception("Provide valid command to execute")

        steps: list[InteractionStep] = []
        elements: list[BrowserElement] = []
        page = await self.context.new_page()

        for i in range(20):
            print(f"Executing step {i + 1}")

            attempts = 1
            current_step = await self.generate_next_step(
                command, steps, list(variables.keys()), elements
            )
            success, message, is_last_step = await self.execute_code(
                page, current_step.code_body, variables
            )

            print(f"Step {i + 1}, Attempt {attempts} result: {message}")

            while not success and attempts < 3:
                print(f"Attempt {attempts} failed:\n{message}")
                success, message, current_step, is_last_step = await self._retry_step(
                    page, command, steps, variables, current_step.code_body, message
                )
                attempts += 1
                print(f"Step {i + 1}, Attempt {attempts} result: {message}")

            if not success:
                print(f"Step {i + 1} failed after {attempts} attempts")
                break

            elements = await self.detect_interactive_elements(page)
            await self.visualize_interactive_elements(page, elements)

            current_step._elements = elements
            steps.append(current_step)

            if is_last_step:
                print(f"Reached last step at step: {i + 1}")
                break

            if i >= 10:
                await asyncio.sleep(10)

        return BrowserSession(
            id=uuid.uuid4(),
            steps=steps,
            user_command=command,
        )

    async def execute_code(
        self, page, code_body: str, variables: dict
    ) -> Tuple[bool, str, bool]:
        namespace = {}

        function_code = f"""{code_body}"""

        try:
            exec(function_code, globals(), namespace)
            dynamic_function = namespace["dynamic_function"]
            return await dynamic_function(page, variables)
        except Exception as e:
            return False, traceback.format_exc(), False
