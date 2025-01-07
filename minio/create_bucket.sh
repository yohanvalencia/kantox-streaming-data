#! /bin/bash

docker exec minio-storage mc alias set minio http://localhost:9000 minioadmin minioadmin
sleep 0.2
docker exec minio-storage mc mb minio/acme.eu-west-1.stg.data.lake