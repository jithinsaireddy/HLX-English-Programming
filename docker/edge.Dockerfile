FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .[iot]
CMD ["python", "-m", "english_programming.hlx.edge_module", "--spec", "english_programming/examples/boiler_a.hlx", "--endpoint", "mqtt://broker"]


