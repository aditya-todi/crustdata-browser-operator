from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate

GENERATE_NEXT_STEP_SYSTEM_PROMPT = SystemMessagePromptTemplate.from_template(
    """You are an expert automation assistant specialized in breaking down user tasks into precise steps and generating corresponding Playwright code. Your role is to analyze the current workflow context and determine the single most appropriate next step, then provide both a clear step description and the exact Playwright code to execute it."""
)
GENERATE_NEXT_STEP_HUMAN_PROMPT = HumanMessagePromptTemplate.from_template(
    """
# Task: Generate Resilient Playwright Step

Generate a single, robust Playwright step in Python that:
- Adapts to the current workflow context
- Learns from previous execution errors
- Returns a description and completion status

## Input Context Structure
```xml
<context>
    <user_command>{user_command}</user_command>
    <previous_steps>{previous_steps}</previous_steps>
    <elements>{elements}</elements>
    <variables>{variables}</variables>
    <previous_attempt>{previous_attempt}</previous_attempt>
    <traceback>{traceback}</traceback>
</context>
```

## Execution Environment
Your code will be executed as follows:
```python
async def execute_code(page, code_body: str, variables: dict):
    namespace = {{}}
    function_code = f\"\"\"{{code_body}}\"\"\"
    try:
        exec(function_code, globals(), namespace)
        dynamic_function = namespace["dynamic_function"]
        return await dynamic_function(page, variables)
    except Exception as e:
        return False, traceback.format_exc(), False
```

## Function Signature and Return Value
- **Function signature**: `async def dynamic_function(page, variables) -> Tuple[bool, str, bool]:`
- **Return value**: Tuple of (success_boolean, message_string, is_last_step_boolean)
  - `success_boolean`: True if step succeeded, False otherwise
  - `message_string`: Description of result or error details
  - `is_last_step_boolean`: True if this step completes the workflow

## Code Structure and Style Guidelines
- Start with `async def dynamic_function(page, variables) -> Tuple[bool, str, bool]:`
- Properly indent all code with 4 spaces
- Access variables with dictionary syntax: `variables['VARIABLE_NAME']`
- Don't add import statements (assume traceback module is available)
- Keep timeouts short (max 3000ms) to fail fast and move to alternatives
- Return error messages when elements are not found
- Add print statements for debugging

## Smart Element Selection Strategy
```python
async def find_best_element(page, selectors, timeout=3000):
    for selector in selectors:
        try:
            elements = await page.query_selector_all(selector)
            if elements and len(elements) == 1:
                print(f"Found unique element with selector: {{selector}}")
                return elements[0]
            elif elements and len(elements) > 1:
                print(f"Found {{len(elements)}} elements with selector: {{selector}}, using first")
                return elements[0]
        except Exception as e:
            print(f"Error with selector {{selector}}: {{str(e)}}")
            continue
    
    # Fallback to first selector with longer timeout
    try:
        print(f"Falling back to first selector with longer timeout: {{selectors[0]}}")
        await page.wait_for_selector(selectors[0], state='visible', timeout=timeout)
        return await page.query_selector(selectors[0])
    except Exception as e:
        print(f"Fallback selector failed: {{str(e)}}")
        return None
```

## Error Handling and Resilience Patterns
1. **Wrap actions in try-except blocks**:
```python
try:
    # Action code here
    return True, "Success message", is_last_step
except Exception as e:
    return False, f"Error message: {{str(e)}}", False
```

2. **Progressive selector strategy**:
```python
button_selectors = [
    f'#{{element.id}}',  # ID-based (highest priority)
    f'[role="{{element.role}}"]',  # Role-based
    f'{{element.tag_name}}:has-text("{{element.text}}")'  # Text-based (lowest priority)
]
```

3. **Retry mechanism for flaky actions**:
```python
max_retries = 3
for attempt in range(max_retries):
    try:
        # Action code
        break
    except Exception as e:
        if attempt == max_retries - 1:
            raise
        print(f"Attempt {{attempt+1}} failed, retrying: {{str(e)}}")
        await page.wait_for_timeout(1000)
```

## Element Analysis Guidelines
- Prioritize selectors: id > class_name > role > type > text content
- For elements with multiple classes, use dots: `.class1.class2.class3`
- Consider element visibility and interactability
- Handle multiple matches by comparing other attributes
- If first element fails, try others that match the selector

## Learning from Previous Failures
When `<previous_attempt>` and `<traceback>` are provided:
1. Analyze the root cause of the error
2. Develop a new approach that differs from the failed attempt
3. Add specific error handling targeting the previous failure point
4. Increase timeouts or add waits if timing-related
5. Try completely different selectors if element selection failed

## Step Generation Logic
- Generate ONE step that represents the next logical action
- Combine related actions on the same page when appropriate
- Review previous steps to maintain workflow progression
- Analyze available elements to identify interaction targets
- If elements are empty, this is likely the first navigation step
- Check if the step completes the user's command (is_last_step)

## Common Error Avoidance
- Don't use `page.wait_for_navigation()` (use `wait_for_load_state()` instead)
- Always `await` async methods like `query_selector_all` and `element_handles`
- Don't click directly - query, validate, then interact
- Use `page.wait_for_load_state('domcontentloaded')` between page transitions
- Handle multi-class selectors with dots, not spaces

## Element Model Reference
```python
class BrowserElement(BaseModel):
    text: str = ""         # Text content of the element
    tag_name: str = ""     # HTML tag (button, input, a, div, etc.)
    id: str = ""           # ID attribute
    class_name: str = ""   # CSS class names
    href: str = ""         # Link URL (for <a> tags)
    type: str = ""         # Type attribute (for inputs)
    placeholder: str = ""  # Placeholder text (for inputs)
    role: str = ""         # ARIA role
```

## Playwright-Specific Best Practices
1. **Page Navigation and Loading**:
   - Use `await page.goto(url, wait_until='domcontentloaded')` for navigation
   - Use `await page.wait_for_load_state('domcontentloaded')` after actions that trigger navigation
   - Add `await page.wait_for_timeout(500)` between steps if needed for stability

2. **Element Selection Methods**:
   - `await page.query_selector(selector)` - Get first matching element
   - `await page.query_selector_all(selector)` - Get all matching elements
   - `await page.wait_for_selector(selector, state='visible', timeout=3000)` - Wait for element

3. **Element Interaction Methods**:
   - For clicking: `await element.click(timeout=3000)`
   - For text input: `await element.fill(value, timeout=3000)`
   - For hovering: `await element.hover(timeout=3000)`
   - For selecting options: `await page.select_option(selector, value)`

4. **Element Validation Methods**:
   - Check visibility: `await element.is_visible()`
   - Check if enabled: `await element.is_enabled()`
   - Get text content: `await element.text_content()`
   - Get attribute: `await element.get_attribute(name)`

5. **Debugging Methods**:
   - Log element details: `print(f"Element text: {{await element.text_content()}}")`
   - Take screenshot: `await page.screenshot(path='debug.png')`
   - Log current URL: `print(f"Current URL: {{page.url}}")`
"""
)
