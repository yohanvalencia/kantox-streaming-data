#! /bin/bash

docker exec spark-master /opt/bitnami/spark/bin/spark-submit --packages org.apache.spark:spark-avro_2.12:3.3.2,org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 /opt/spark-apps/spark_streaming.py >/dev/null 2>&1 &
