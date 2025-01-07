-- CREATE STREAM latest_events ( id BIGINT, type STRING, event STRUCT< customer_id BIGINT, timestamp STRING >, metadata STRUCT< correlation_id STRING, timestamp STRING, schema_id BIGINT > ) WITH ( KAFKA_TOPIC='acme.clickstream.latest.events', VALUE_FORMAT='AVRO' );

CREATE STREAM latest_events WITH (
    KAFKA_TOPIC='acme.clickstream.latest.events', 
    VALUE_FORMAT='AVRO',
    VALUE_SCHEMA_ID=2
);

DROP STREAM latest_events;

CREATE STREAM latest_events (
    event STRUCT<
        customer_id BIGINT,
        timestamp STRING
    >
) WITH ( 
    KAFKA_TOPIC='acme.clickstream.latest.events',
    VALUE_FORMAT='AVRO'
);
