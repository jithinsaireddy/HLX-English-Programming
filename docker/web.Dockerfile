FROM python:3.11-slim
WORKDIR /app

# Copy project first to leverage Docker layer caching
COPY . /app

# Install runtime deps: gunicorn + project with NLP extras, then fetch spaCy model
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir gunicorn \
 && pip install --no-cache-dir -e .[nlp] \
 && python -m spacy download en_core_web_sm

# App runtime configuration
ENV EP_ENABLE_NET=0
ENV EP_MAX_OPS=200000
ENV EP_MAX_MS=30000
ENV PYTHONUNBUFFERED=1

# Expose default port (can be overridden by PORT env)
EXPOSE 5000

# Allow overriding worker count and port via env
ENV WEB_CONCURRENCY=2
ENV PORT=5000

# Use sh -c so ${PORT} and ${WEB_CONCURRENCY} are expanded
CMD ["sh", "-c", "gunicorn -w ${WEB_CONCURRENCY:-2} -b 0.0.0.0:${PORT:-5000} english_programming.src.interfaces.web.web_app:app"]


