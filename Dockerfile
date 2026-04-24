FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir -e .

COPY configs ./configs
COPY examples ./examples

EXPOSE 8000

CMD ["uvicorn", "manugent.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
