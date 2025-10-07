FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies (project + runtime server)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn && \
    python -m spacy download en_core_web_sm

# Copy application
COPY wsgi.py /app/
COPY english_programming /app/english_programming

# Beanstalk forwards to PORT env; set sane defaults
ENV PORT=8000
ENV WEB_CONCURRENCY=1
EXPOSE 8000

# Use sh -c so ${PORT} and ${WEB_CONCURRENCY} expand at runtime
CMD ["sh", "-c", "gunicorn wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-1} --timeout 120"]
