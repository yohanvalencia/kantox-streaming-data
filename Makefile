SHELL := /bin/bash

all: create_bucket create_topics register_schemas add_connectors create_ksql

.PHONY: add_connectors
add_connectors:
	@cd connectors && ./add_connectors.sh

.PHONY: create_bucket
create_bucket:
	@cd minio && ./create_bucket.sh

.PHONY: register_schemas
register_schemas:
	@cd schemas && ./register_schemas.sh

.PHONY: create_topics
create_topics:
	@cd topics && ./create_topics.sh

.PHONY: create_ksql
create_ksql:
	@cd kafka_streams && ./create_stream_and_table.sh
	
.PHONY: start_spark
start_spark:
	@cd pyspark/apps && ./run_spark_streaming.sh
	@ echo Spark process running in the background

.PHONY: stop_spark
stop_spark:
	@docker exec spark-master bash -c "/bin/bash /opt/spark-apps/stop_spark_streaming.sh"
