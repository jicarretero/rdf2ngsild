from kafka import KafkaConsumer
from config_translator import ConfigTranslator


class KafkaReader:
    def __init__(self):
        # Consumer configuration
        self.consumer_config = {
            'bootstrap.servers': ConfigTranslator().get_string("kafka-client", "servers"),
            # Replace with the correct address if necessary
            'group.id': 'python-consumer',
            'auto.offset.reset': 'earliest'  # Start reading from the first available message
        }
        self.bootstrap_servers = ConfigTranslator().get_string("kafka-client", "servers")
        self.topic = ConfigTranslator().get_string("kafka-client", "topic")
        print("READER topic:", self.topic)

        self.consumer = KafkaConsumer(bootstrap_servers=[self.bootstrap_servers],
                                      auto_offset_reset='earliest',
                                      enable_auto_commit=True,
                                      group_id='my-group',
                                      consumer_timeout_ms=ConfigTranslator().get_interger(
                                          "kafka-client", "reader_timeout"),
                                      value_deserializer=lambda x: x.decode('utf-8'))

        self.consumer.subscribe(topics=[self.topic])
        self.stop = False

    def stop_it(self):
        self.stop = True

    def consume_messages(self):
        while True:
            for message in self.consumer:
                yield message.value

            print("Saliendo del bucle {message}!")
        # Close the consumer
        self.consumer.close()

    def consume_one(self):
        # Wait for messages
        return next(self.consumer)

    def commit(self):
        self.consumer.commit()


if __name__ == "__main__":
    KafkaReader.consume_messages()
