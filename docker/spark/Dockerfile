# Thoughts: I update the spark version so it was compatible with amd and arm architectures.
ARG SPARK_VERSION=3.3.2

FROM bitnami/spark:${SPARK_VERSION}

# Install Python libraries
RUN pip3 install --no-cache-dir \
    pyspark \
    confluent-kafka[avro,schemaregistry] \
    pyarrow \
    fastavro
