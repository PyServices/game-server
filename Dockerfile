# Django-Back - Hamravesh/Kubernetes deployment
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps (psycopg2, Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files (for admin)
RUN python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8000

# Daphne for HTTP + WebSockets (Channels)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
