from kafka import TopicPartition
import json

def kafka_pull_data(topic, consumer):
    # Poll for Kafka messages
    partitions = consumer.partitions_for_topic(topic)
    # start = time.time() 
    # messages = self.odom_consumer.poll(timeout_ms=10)
                # print("Received message: {}".format(message.value))
    last_offsets = {p: offset-1 for p in partitions for offset in consumer.end_offsets([TopicPartition(topic, p)]).values()}

    for p, last_offset in last_offsets.items():
        start_offset = max(0, last_offset - 1 + 1)
        tp = TopicPartition(topic, p)
        consumer.assign([tp])
        consumer.seek(tp, start_offset)
    # start = time.time()
    messages = consumer.poll(timeout_ms=1000)  # Wait for 1000ms

    if messages:
        for tp, msgs in messages.items():
            for message in msgs:
                # print("Received message: {}".format(message.value))
                decoded_message = message.value.decode('utf-8')  # Decode the bytes to string
                data = json.loads(decoded_message)  # Convert the JSON string to a dictionary
                # print("Received message: {}".format(data))
                
    else:
        print("No message received within timeout period")
    return data

                
                