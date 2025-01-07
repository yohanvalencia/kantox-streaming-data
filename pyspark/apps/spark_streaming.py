import logging as log
from typing import Union

import pyspark.sql.functions as f
from pyspark.sql import SparkSession
from pyspark.sql.avro.functions import from_avro, to_avro
from pyspark.sql.types import StringType, BinaryType
from confluent_kafka.schema_registry import SchemaRegistryClient
from pyspark.sql.dataframe import DataFrame
from confluent_kafka.schema_registry.schema_registry_client import Schema

# Kafka Configuration
KAFKA_BROKERS = 'kafka0:29092'
KAFKA_CHECKPOINT = 'checkpoint'

# App Configuration
ACME_PYSPARK_APP_NAME = 'AcmeSparkStreaming'
CLICKSTREAM_RAW_EVENTS_TOPIC = 'acme.clickstream.raw.events'
CLICKSTREAM_LATEST_EVENTS_TOPIC = 'acme.clickstream.latest.events'
CLICKSTREAM_RAW_EVENTS_SUBJECT = f'{CLICKSTREAM_RAW_EVENTS_TOPIC}-value'
SCHEMA_REGISTRY_URL = "http://schema-registry0:8085"

packages = ['org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0',
            'org.apache.spark:spark-avro_2.12:3.3.0']

# Initialize logging
log.basicConfig(level=log.INFO,
                format='%(asctime)s [%(levelname)s] [%(name)8s] %(message)s')
logger = log.getLogger('acme_pyspark')

# UDFs
binary_to_string_udf = f.udf(lambda x: str(int.from_bytes(x, byteorder='big')), StringType())
int_to_binary_udf = f.udf(lambda value, byte_size: value.to_bytes(byte_size, byteorder='big'), BinaryType())

def initialize_spark_session(app_name: str) -> Union[SparkSession, None]:
    """
    Initialize the Spark Session with provided configurations.

    :param app_name: Name of the spark application.
    :return: Spark session object or None if there's an error.
    """
    try:
        spark = SparkSession.builder \
            .appName(app_name) \
            .master('spark://spark-master:7077') \
            .config('spark.jars.packages', ','.join(packages)) \
            .config('spark.sql.adaptive.enabled', 'false') \
            .getOrCreate()

        spark.sparkContext.setLogLevel("WARN")
        logger.info('Spark session initialized successfully')
        return spark

    except Exception as e:
        logger.error(f"Spark session initialization failed. Error: {e}")
        return None

def get_avro_schema(schema_registry_url: str, subject: str) -> Union[Schema, None]:
    """
    Fetch the latest Avro schema from the Schema Registry.

    :param schema_registry_url: URL of the Schema Registry.
    :param subject: Schema subject.
    :return: Schema object.
    """
    try:
        client = SchemaRegistryClient({'url': schema_registry_url})
        latest_schema = client.get_latest_version(subject)
        logger.info(f"Fetched Avro schema for {subject}.")
        return latest_schema
    except Exception as e:
        logger.error(f"Failed to fetch schema for {subject}. Error: {e}")
        return None

def get_streaming_dataframe(spark: SparkSession, brokers: str, topic: str) -> Union[DataFrame, None]:
    """
    Get a streaming dataframe from Kafka.

    :param spark: Initialized Spark session.
    :param brokers: Comma-separated list of Kafka brokers.
    :param topic: Kafka topic to subscribe to.
    :return: Dataframe object or None if there's an error.
    """
    try:
        raw_stream = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", brokers) \
            .option("subscribe", topic) \
            .option("startingOffsets", "latest") \
            .option("includeHeaders", "true") \
            .option("kafkaConsumer.pollTimeoutMs", "3000") \
            .load()

        logger.info("Streaming dataframe initialized successfully")
        return raw_stream

    except Exception as e:
        logger.error(f"Failed to initialize streaming dataframe. Error: {e}")
        return None

def transform_streaming_data(raw_stream: DataFrame, des_schema: Schema, ser_schema: Schema) -> Union[DataFrame, None]:
    """
    Transform the initial dataframe to get the final structure.

    :param raw_stream: Initial dataframe with raw data.
    :param des_schema: Deserialization schema.
    :param ser_schema: Serialization schema.
    :return: Transformed dataframe.
    """
    try:
        raw_stream = raw_stream.withColumn(
            "headers",
            f.map_from_entries(f.expr(
                "transform(headers, x -> struct(x.key as key, cast(x.value as string) as value))"
            ))
        )

        # Thoughts: This was needed because confluent kafka makes changes to the binary data adding
        # a magic byte (1 byte) + schema id (4 bytes) + payload
        # https://medium.com/@mrugankray/real-time-avro-data-analysis-with-spark-streaming-and-confluent-kafka-in-python-426f5e05392d
        raw_stream = raw_stream.withColumn("correlation_id", f.col("headers.X-Correlation-ID"))
        raw_stream = raw_stream.withColumn("fixedValue", f.expr("substring(value, 6, length(value) - 5)"))
        raw_stream = raw_stream.withColumn('valueSchemaId', binary_to_string_udf(f.expr("substring(value, 2, 4)")))
        raw_stream = raw_stream.withColumn("schema_id", f.col("valueSchemaId").cast("long"))
    
        event_data = raw_stream.select(
            from_avro(f.col("fixedValue"), des_schema.schema.schema_str).alias("data"),
            "correlation_id",
            "schema_id",
            "timestamp"
        )

        transformed_df = event_data.select(
            f.col("data.id").cast("long").alias("id"),
            f.col("data.type").alias("type"),
            f.col("data.event").alias("event"),
            f.struct(
                f.col("correlation_id"),
                f.col("timestamp").cast("string").alias("timestamp"),
                f.col("schema_id")
            ).alias("metadata")
        )

        # Thoughts: This part took me some time but then I realised I had to add the extra bytes
        # https://github.com/mrugankray/Spark_Streaming_with_kafka/blob/main/2_real-time_avro_data_analysis_with_spark_streaming_and_confluent_kafka_in_python/avro_wikimedia_spark_consumer.py
        binary_data = transformed_df.select(to_avro(f.struct(transformed_df.columns), ser_schema.schema.schema_str).alias("value"))
        magic_byte = int_to_binary_udf(f.lit(0), f.lit(1))
        schema_id_binary = int_to_binary_udf(f.lit(ser_schema.schema_id), f.lit(4))
        binary_data = binary_data.withColumn("value", f.concat(magic_byte, schema_id_binary, f.col("value")))

        logger.info("Streaming data transformed successfully")
        return binary_data

    except Exception as e:
        logger.error(f"Data transformation failed. Error: {e}")
        return None

def initiate_streaming_to_topic(df: DataFrame, brokers: str, topic: str, checkpoint: str) -> None:
    """
    Start streaming the transformed data to the specified Kafka topic.

    :param df: Transformed dataframe.
    :param brokers: Kafka brokers.
    :param topic: Kafka topic to publish to.
    :param checkpoint: Checkpoint location.
    :return: None
    """
    try:
        logger.info(f"Streaming to topic {topic} with checkpoint at {checkpoint}")
        df.selectExpr("CAST(NULL as STRING) AS key", "value") \
            .writeStream \
            .outputMode("append") \
            .format("kafka") \
            .option("kafka.bootstrap.servers", brokers) \
            .option("topic", topic) \
            .option("checkpointLocation", checkpoint) \
            .start() \
            .awaitTermination()
    except Exception as e:
        logger.error(f"Failed to stream data to topic {topic}. Error: {e}")

def main() -> None:
    spark = initialize_spark_session(ACME_PYSPARK_APP_NAME)
    if spark:
        des_schema = get_avro_schema(SCHEMA_REGISTRY_URL, CLICKSTREAM_RAW_EVENTS_TOPIC)
        ser_schema = get_avro_schema(SCHEMA_REGISTRY_URL, CLICKSTREAM_LATEST_EVENTS_TOPIC)

        if des_schema and ser_schema:
            df = get_streaming_dataframe(spark, KAFKA_BROKERS, CLICKSTREAM_RAW_EVENTS_TOPIC)
            if df:
                transformed_df = transform_streaming_data(df, des_schema, ser_schema)
                if transformed_df:
                    initiate_streaming_to_topic(
                        transformed_df, KAFKA_BROKERS, CLICKSTREAM_LATEST_EVENTS_TOPIC, KAFKA_CHECKPOINT)

if __name__ == '__main__':
    main()