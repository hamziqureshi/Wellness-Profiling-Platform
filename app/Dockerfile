
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["sh", "-c", "uvicorn app:app --host ${HOST} --port ${FAST_API_PORT} --workers ${WORKERS}"]
