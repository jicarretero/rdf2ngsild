# from confluent_kafka import Producer, KafkaException
# from confluent_kafka.admin import AdminClient
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from config_translator import ConfigTranslator
import uuid


class KafkaWriter:
    def __init__(self):
        """
        Commodity class for testing. This will write data to a kafka topic depeding on the parameters configurd in the
        cofiguration file.
        """
        self.bootstrap_servers = ConfigTranslator().get_string("kafka-client", "servers")

        # Topic name
        self.topic_name = ConfigTranslator().get_string("kafka-client", "topic")

        self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)

    def __remove_topics(self):
        """
        Remove topics from kafka.

        :return:
        """
        print("Removing topics!")
        ac = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        ac.delete_topics([self.topic_name])
        ac.create_topics(new_topics=[NewTopic(name=self.topic_name,
                                              num_partitions=1, replication_factor=1)])
        # ac = AdminClient(self.producer_config)
        # ac.delete_topics([self.topic_name])

    def uuid(self):
        """

        :return: uuid64 as string.
        """
        return str(uuid.uuid4())

    def on_delivery(self, err, msg):
        """
        Method call when the message is delivered to a kafka queue.

        :param err:
        :param msg:
        :return:
        """
        if err is not None:
            print('Delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(
                msg.topic(), msg.partition()))

    def produce_message(self, data: str):
        """
        Send a message to the Kafka queue.

        :param data:
        :return:
        """
        # Sending a message to the topic (synchronous)
        ba = data.encode('utf-8')
        self.producer.send(topic=self.topic_name, value=ba)
        self.producer.flush()

