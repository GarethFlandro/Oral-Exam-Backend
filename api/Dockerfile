FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Use the PORT env variable provided by Cloud Run
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}