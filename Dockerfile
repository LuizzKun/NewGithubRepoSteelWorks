FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install runtime dependencies first for better Docker layer caching.
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Install sentry runtime dependency added via Poetry.
RUN pip install sentry-sdk

# Copy application source.
COPY . /app

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "src/steelworks/app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
