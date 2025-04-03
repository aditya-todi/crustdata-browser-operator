#!/bin/bash

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m playwright install
python -m langchain_openai install
