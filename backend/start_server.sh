#!/bin/bash
cd "$(dirname "$0")"
../venv/bin/python -m uvicorn main:app --reload --port 8001
