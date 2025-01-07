#!/bin/bash

# Thoughts: I couldn't find a way to set the 
# stream to the schema id that was originally created.
# not sure if it is related to the schema evolution in the shema registry.
# I would need to research further, but at least this way the task is achieved.
# Also, it might be importart to set a tumbling window.
curl -X "POST" "http://localhost:8088/ksql" \
     -H "Content-Type: application/vnd.ksql.v1+json; charset=utf-8" \
     --data-binary $'{"ksql": "CREATE STREAM latest_events WITH (KAFKA_TOPIC=\'acme.clickstream.latest.events\', VALUE_FORMAT=\'AVRO\', VALUE_SCHEMA_ID=2);", "streamsProperties": {}}' > /dev/null 2>&1

sleep 0.5

curl -X "POST" "http://localhost:8088/ksql" \
     -H "Content-Type: application/vnd.ksql.v1+json; charset=utf-8" \
     --data-binary $'{"ksql": "DROP STREAM latest_events;", "streamsProperties": {}}' > /dev/null 2>&1

sleep 0.5

curl -X "POST" "http://localhost:8088/ksql" \
     -H "Content-Type: application/vnd.ksql.v1+json; charset=utf-8" \
     --data-binary $'{"ksql": "CREATE STREAM latest_events (event STRUCT<customer_id BIGINT, timestamp STRING>) WITH (KAFKA_TOPIC=\'acme.clickstream.latest.events\', VALUE_FORMAT=\'AVRO\');", "streamsProperties": {}}' > /dev/null 2>&1

sleep 0.5

curl -X "POST" "http://localhost:8088/ksql" \
     -H 'content-type: application/vnd.ksql.v1+json; charset=utf-8' \
     -d "{\"ksql\": \"$(cat unique_customer_id_per_day.sql)\", \"streamsProperties\": {}}" > /dev/null 2>&1

echo "Stream and table created!"