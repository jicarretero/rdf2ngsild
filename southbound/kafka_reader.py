from kafka import KafkaConsumer
from config_translator import ConfigTranslator
import logging

log = logging.getLogger(__name__)


class KafkaReader:
    """
    Class implementing a Kafka Reader. This reader will get data from Kafka and it will Yield all the messages read.
    """

    def __init__(self):
        """
        Initializes the Object with the configuration in the config file
        """
        # Consumer configuration
        self.bootstrap_servers = ConfigTranslator().get_string("kafka-client", "servers")
        self.topic = ConfigTranslator().get_string("kafka-client", "topic")
        log.debug("READER topic: %s" % (self.topic))

        self.consumer = KafkaConsumer(bootstrap_servers=[self.bootstrap_servers],
                                      auto_offset_reset='earliest',
                                      enable_auto_commit=True,
                                      group_id='my-group',
                                      consumer_timeout_ms=ConfigTranslator().get_interger(
                                          "kafka-client", "reader_timeout"),
                                      value_deserializer=lambda x: x.decode('utf-8'))

        self.consumer.subscribe(topics=[self.topic])

        self.is_benchmark = False
        self.max_messages = ConfigTranslator().get_interger(
            "kafka-demo", "max_messages_sent")

    def consume_messages(self):
        """
        Methods that reads messages from Kafka and yields them to be processed. It will only stop iterating
        in benchmarks.

        :return:
        """
        stay_in = True
        benchmark = self.is_benchmark
        max_messages = self.max_messages
        n = 0

        while stay_in:
            for message in self.consumer:
                yield message.value
                n += 1
                log.info("message yielded %d", (n))
                if benchmark and n >= max_messages:
                    stay_in = False
                    break

        # Close the consumer
        self.consumer.close()

    def consume_one(self):
        """
        Method that consumes 1 message at most.

        :return: Message read from Kafka
        """
        # Wait for messages
        return next(self.consumer)

    def commit(self):
        """
        Commits the message as read.

        :return:
        """
        self.consumer.commit()


if __name__ == "__main__":
    for m in KafkaReader.consume_messages():
        print(m)
