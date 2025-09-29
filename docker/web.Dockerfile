FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir gunicorn \
 && pip install --no-cache-dir -e . \
 && python - <<'PY'
try:
    import spacy
    try:
        spacy.load('en_core_web_sm')
    except Exception:
        import os; os.system('python -m spacy download en_core_web_sm')
except Exception:
    pass
PY
ENV EP_ENABLE_NET=0
ENV EP_MAX_OPS=200000
ENV EP_MAX_MS=30000
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "english_programming.src.interfaces.web.web_app:app"]


