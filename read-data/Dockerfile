FROM python:3.8-slim
ENV PYTHONDONTWRITEBYTECODE 1

# Install and setup poetry
RUN pip install -U pip \
    && apt-get update \
    && apt install -y curl netcat \
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH="${PATH}:/root/.poetry/bin"

WORKDIR /app
COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

COPY read_data.py ./read_data.py
COPY api-key.txt ./api-key.txt
ENTRYPOINT ["poetry", "run", "python", "read_data.py"]
