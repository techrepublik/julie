FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for building wheels, then clean
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy project
COPY . /app/

# Collect static (ignore errors if not configured)
RUN python manage.py collectstatic --noinput || true

# Expose internal port
EXPOSE 8000

# Run DB migrations then start Gunicorn
CMD sh -c "python manage.py migrate && gunicorn julie.wsgi:application --bind 0.0.0.0:8000 --workers 3"

