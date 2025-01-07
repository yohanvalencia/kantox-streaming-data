# Kantox Data Engineer Challenge

## Requirements
- Docker Desktop
- pipenv or another virtualenv

## Build and Up the platform
Execute the following command
```
$ cd kantox-data-eng-test
$ docker compose up -d --build
$ docker ps -a
```
You should have the following containers up and running
<pre>
kafka-ui            <a href="http://localhost:8080">http://localhost:8080</a>
kafka-connect0      <a href="http://localhost:8083">http://localhost:8083</a>
schema-registry0    <a href="http://localhost:8085">http://localhost:8085</a>
rest-proxy          <a href="http://localhost:8082">http://localhost:8082</a>
ksqldb-server       <a href="http://localhost:8088">http://localhost:8088</a>
kafka0              <a href="http://localhost:9092">http://localhost:9092</a>
spark-master        <a href="http://localhost:18080">http://localhost:18080</a>
spark-worker-1      <a href="http://localhost:28081">http://localhost:28081</a>
minio-storage       <a href="http://localhost:9000">http://localhost:9000</a>
</pre>

## Shutdown the platform
```
$ docker compose down
```

## Start API Server
To start your API Server execute the following command
```
$ cd api
$ pipenv --python 3.11
$ pipenv shell
$ pip install -r requirements.txt
$ python server.py
```
The default value for port argument is `60000`

## Start the events JSON generator
To start your API Server execute the following command
```
$ cd generator
$ pipenv --python 3.11
$ pipenv shell
$ pip install -r requirements.txt
$ python generator.py
```
The default values for hostname and filename arguments are `localhost:60000` and `../data/events.json`

**Note 1**: Remember to unzip the `..data/events.json.zip` file.

**Note 2**: You can use `JSON Schema`, `Avro Schema` or `Protobuf` for your schema definitions

## Execute Spark Streaming App
To run the Spark Streaming process, follow these steps. Your code should be implemented in the file `/pyspark/apps/spark_streaming.py`, for which we've already provided an initial template.

To avoid installing Spark on your computer, enter the following Docker container using the command:
```
$ docker exec -it spark-master bash
```
Then execute the Spark job with:
```
$ /opt/bitnami/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 /opt/spark-apps/spark_streaming.py
```
You can connect to the master and worker via http://localhost:18080 and http://localhost:28081.

## Tasks TODO

- [ ] Implement the HTTP POST /collect method in `api/pipeline/input.py`
    - [ ] Connect to Schema Registry
    - [ ] Validate and serialize events in JSON
    - [ ] Send valid event to Kafka `acme.clickstream.raw.events`
    - [ ] Send invalid events to Kafka `acme.clickstream.invalid.events`
- [ ] Implement Spark Streaming application to read from Kafka
    - [ ] Deserialize and validate the JSON using Schema Registry
    - [ ] Transform the dataframe to include the new `metadata` field
    - [ ] Send results to another Kafka topic `acme.clickstream.latest.events`
- [ ] Create schema for `acme.clickstream.raw.events` topic
    - [ ] Implement a bash to register schemas in Schema Registry
- [ ] Create connectors to install in Kafka Connect
    - [ ] Implement a bash to create connectors in Kafka
- [ ] Implement a bash to create topics in Kafka
- [ ] Save all events inserted in Kafka topics to Minio
- [ ] **Optional**, Implement Unique Users by day aggregation using KSQL and send results to `acme.clickstream.unique.users`
