FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./pyproject.toml .
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install -E broker

COPY aiplayground /app/aiplayground

ENV MODULE_NAME=aiplayground.app
