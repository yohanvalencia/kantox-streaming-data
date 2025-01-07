# Deploy solution

Before we start we need to unzip data/events.json.zip

1. cd api
2. docker image build -t acme-python-api .
3. cd ..
4. docker compose up -d --build
5. wait a few seconds so all the resources spin-up.
6. make
7. docker compose up -d
8. make start_spark
9. cd generator
10. install dependencies and run the generator.