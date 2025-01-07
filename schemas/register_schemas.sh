
#! /bin/bash

curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" --data '{"schema": "'"$(jq -c . acme.clickstream.raw.events.avsc | sed 's/"/\\\"/g')"'"}' http://localhost:8085/subjects/acme.clickstream.raw.events/versions
sleep 0.2
curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" --data '{"schema": "'"$(jq -c . acme.clickstream.latest.events.avsc | sed 's/"/\\\"/g')"'"}' http://localhost:8085/subjects/acme.clickstream.latest.events/versions


