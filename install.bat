@echo off
python -m venv .venv
python -m pip install poetry
poetry install
pause