# from confluent_kafka import Producer, KafkaException
# from confluent_kafka.admin import AdminClient
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from config_translator import ConfigTranslator
import uuid


class KafkaWriter:
    def __init__(self):
        # Producer configuration
        self.producer_config = {
            # Replace with the correct address if necessary
            'bootstrap.servers': ConfigTranslator().get_string("kafka-client", "servers"),
        }

        self.bootstrap_servers = ConfigTranslator().get_string("kafka-client", "servers")

        # Topic name
        self.topic_name = ConfigTranslator().get_string("kafka-client", "topic")

        self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)

        # self.__remove_topics()

    def __remove_topics(self):
        print("Removing topics!")
        ac = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        ac.delete_topics([self.topic_name])
        ac.create_topics(new_topics=[NewTopic(name=self.topic_name,
                                              num_partitions=1, replication_factor=1)])
        # ac = AdminClient(self.producer_config)
        # ac.delete_topics([self.topic_name])

    def uuid(self):
        return str(uuid.uuid4())

    def on_delivery(self, err, msg):
        if err is not None:
            print('Delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(
                msg.topic(), msg.partition()))

    def produce_message(self, data: str):
        # Sending a message to the topic (synchronous)
        ba = data.encode('utf-8')
        print("Writing data to ", self.topic_name)
        self.producer.send(topic=self.topic_name, value=ba)
        self.producer.flush()


if __name__ == "__main__":
    KafkaWriter().produce_message()
