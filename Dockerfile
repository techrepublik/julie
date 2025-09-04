FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

# System deps for wheels + runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Isolated venv (smaller/faster)
RUN python -m venv /venv

WORKDIR /app

# Install deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy project
COPY . /app/

# Gunicorn config (copied now; created below)
COPY gunicorn.conf.py /app/gunicorn.conf.py

# Entrypoint handles wait-for-db, migrate, collectstatic
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "julie.wsgi:application", "-c", "gunicorn.conf.py"]
