FROM python:3.9-slim as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM python:3.9-slim

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

COPY carpi /app/carpi

WORKDIR /app

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

ENV PYTHONPATH /app

EXPOSE 80

CMD [ "uvicorn", "carpi.main:app", "--host", "0.0.0.0", "--port", "80" ]	