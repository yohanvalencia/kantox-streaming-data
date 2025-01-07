#! /bin/bash
curl -X POST -H "Content-Type: application/json" --data @acme.eu.clickstream.raw.s3.sink.json http://localhost:8083/connectors
sleep 0.2
curl -X POST -H "Content-Type: application/json" --data @acme.eu.clickstream.invalid.s3.sink.json http://localhost:8083/connectors
sleep 0.2
curl -X POST -H "Content-Type: application/json" --data @acme.eu.clickstream.unique.users.s3.sink.json http://localhost:8083/connectors