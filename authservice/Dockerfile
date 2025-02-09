FROM python:3.11-slim

ARG BUILD_NO_CACHE
WORKDIR /app

COPY requirements.txt .
RUN if [ "$BUILD_NO_CACHE" = "true" ]; then pip install --no-cache-dir -r requirements.txt; else pip install -r requirements.txt; fi

COPY . .


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
