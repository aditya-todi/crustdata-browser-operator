# Browser Operator

## Overview

Browser Operator is a project designed to interact with web pages using Playwright and Langchain. It leverages AI models from OpenAI and Anthropic to generate and execute interaction steps on web pages.

## Setup and Installation

Follow these steps to set up and run the project:

### 1. Create .env File

Create a `.env` file in the root directory of the project with the following variables. You can use the `.env.example` file as a reference.

### 2. Install Dependencies

Give execute permissions to the `install.sh` script.

```bash
chmod +x scripts/install.sh
```

Run the `install.sh` script to create a virtual environment and install the required dependencies.

```bash
./scripts/install.sh
```

### 3. Run the Project

Give execute permissions to the `run.sh` script.

```bash
chmod +x scripts/run.sh
```

Run the `run.sh` script to start the project.

```bash
./scripts/run.sh
```

## Usage

The Browser Operator exposes an API that can be used to interact with web pages. Follow these steps to use the API:

1. Start the server using the instructions above
2. Open the Swagger documentation at http://127.0.0.1:10000/docs
3. Use the `/interact/start` endpoint to initiate a browser session
4. Variables contains the sensitive information that is not sent to LLM but referenced as local variables for increased security
5. Model is the model to be used for the interaction. Currently, only `anthropic` and `openai` are supported.

### Example Request

You can send a POST request to `/interact/start` with a payload like this:

```json
{
  "command": "open hugging face and login to my account, search 'stable diffusion 3.5 large' and open the model and generate image for 'interstellar black hole' on the model page",
  "variables": {
     "username": "",
     "password": ""
  },
  "model": "anthropic"
}
```
