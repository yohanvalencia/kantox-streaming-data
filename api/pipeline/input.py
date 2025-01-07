import json
import logging
import os
from typing import Dict, List
from uuid import uuid4
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField

from pipeline.headers import HeadersBuilder


# Initialize env vars
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL")
SCHEMA_NAME = os.getenv("SCHEMA_NAME")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_RAW_TOPIC = os.getenv("KAFKA_RAW_TOPIC")
KAFKA_INVALID_TOPIC = os.getenv("KAFKA_INVALID_TOPIC")
PRODUCER_CONFIG_COMPRESSION_TYPE = os.getenv("PRODUCER_CONFIG_COMPRESSION_TYPE")
PRODUCER_CONFIG_MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION = os.getenv("PRODUCER_CONFIG_MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION")

# Initialize Schema Registry Client
schema_registry_client = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})
schema_metadata = schema_registry_client.get_latest_version(SCHEMA_NAME)
schema_definition = schema_metadata.schema.schema_str
schema_version = schema_metadata.version

# Initialize Avro Serializer
avro_serializer = AvroSerializer(
    schema_registry_client,
    schema_definition,
    lambda obj, ctx: obj,
)

# Thoughts: Config improvements covered in page 50
producer_config = {
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
    "compression.type": PRODUCER_CONFIG_COMPRESSION_TYPE,
    "max.in.flight.requests.per.connection": PRODUCER_CONFIG_MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION,
}
producer = Producer(producer_config)


# Return messages
OK = {"status": "OK"}
ERROR_JSON_ARRAY = {"status": "error", "message": "Payload must be a JSON array."}


def collect(events: List[Dict]) -> Dict[str, str]:
    """Handle data collection events.

    :param events: List of events to process
    :return: Confirmation message
    """
    if not isinstance(events, list):
        return ERROR_JSON_ARRAY

    correlation_id = str(uuid4())
    logging.info(f"Collecting data with correlation id: {correlation_id}")

    for evt in events:
        try:
            # Thoughts: I'm not assigning a partition key because we're sending raw data to this topic. 
            # The goal is to allow scaling out if traffic increases and we need to add more consumers to 
            # our consumer groups without worrying about where the next events will land. Note that the 
            # number of consumers in a consumer group cannot exceed the number of partitions. 
            # Having more consumers than partitions will make the extra ones be idle.
            #
            # Initially, I considered partitioning by event type. However, upon further review, the 
            # most probable partition with a higher volume of events would likely be 'page_view', 
            # leading to an imbalance. Custom partitioning was another option I considered, as described 
            # in the book on page 60, 'Chapter 3: Kafka Producers: Writing Messages to Kafka'. 
            # However, without a deeper understanding of the business domain, I decided to stick with 
            # this approach for now.
            #
            # Side note: I initially believed the broker used round-robin distribution across partitions. 
            # However, it seems the distribution is now influenced by the producer's throughput.

            headers = (
                HeadersBuilder()
                .addCorrelationId(correlation_id)
                .build()
            )

            producer.produce(
                topic=KAFKA_RAW_TOPIC,
                value=avro_serializer(evt, SerializationContext(KAFKA_RAW_TOPIC, MessageField.VALUE)),
                headers=headers,
            )
        except Exception as e:
            logging.error(f"Event validation failed with correlation id: {correlation_id}")
            headers = (
                HeadersBuilder()
                .addCorrelationId(correlation_id)
                .addErrorMessage(str(e))
                .build()
            )
            
            producer.produce(
                topic=KAFKA_INVALID_TOPIC,
                value=json.dumps(evt).encode("utf-8"),
                headers=headers,
            )

    producer.flush()
    return OK
