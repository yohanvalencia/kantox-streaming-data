# I used the sample code from 
# https://github.com/confluentinc/confluent-kafka-python?tab=readme-ov-file#basic-adminclient-example

import csv
from confluent_kafka.admin import AdminClient, NewTopic

a = AdminClient({'bootstrap.servers': 'localhost:9092'})

# Note: In a multi-cluster production scenario, it is more typical to use a replication_factor of 3 for durability.
new_topics = [
    NewTopic(topic=row[0], num_partitions=int(row[1]), replication_factor=int(row[2]))
    for row in csv.reader(open('clickstream', 'r'))]

# Call create_topics to asynchronously create topics. A dict
# of <topic,future> is returned.
fs = a.create_topics(new_topics)

# Wait for each operation to finish.
for topic, f in fs.items():
    try:
        f.result()  # The result itself is None
        print("Topic {} created".format(topic))
    except Exception as e:
        print("Failed to create topic {}: {}".format(topic, e))