FROM python:3.11-slim-buster
WORKDIR /api
ENV SCHEMA_REGISTRY_URL=http://localhost:8085
ENV SCHEMA_NAME=acme.clickstream.raw.events
ENV KAFKA_BOOTSTRAP_SERVERS=localhost:9092
ENV KAFKA_RAW_TOPIC=acme.clickstream.raw.events
ENV KAFKA_INVALID_TOPIC=acme.clickstream.invalid.events
ENV PRODUCER_CONFIG_COMPRESSION_TYPE=snappy
ENV PRODUCER_CONFIG_MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION=1
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 60000
CMD ["python", "server.py"]