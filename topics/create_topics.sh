#!/bin/bash
while IFS=, read -r topic partitions replication || [[ -n "$topic" ]]; do
    docker exec kafka0 kafka-topics --create --bootstrap-server localhost:9092 --replication-factor $replication --partitions $partitions --topic $topic >/dev/null 2>&1
    sleep 0.2
    echo "Topic '$topic' created with $partitions partitions and $replication replication."
done < clickstream
