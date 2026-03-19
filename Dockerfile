FROM python:3.11-slim

WORKDIR /app

# copy requirements file
COPY requirements.txt .

# install dependencies from requirements file
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest
COPY . . 

# start app
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
