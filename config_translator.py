import configparser
import json

class ConfigTranslator:
    """
    Singleton Class which reads the configuration from the configuration file and can retrieve configuration values

    """
    instance = None

    class __ConfigTranslator:
        def __init__(self, filename):
            """
            Reads the filename and sets the config parser

            :param filename:
            """
            self.config = configparser.ConfigParser()
            self.filename = filename
            self.config.read(filename)

        def get_string(self, block, name):
            """
            Return a String from the configuration parser

            :param block:
            :param name:
            :return: String value from the configuration parser or "" as default value.
            """
            try:
                return self.config.get(block, name)
            except configparser.NoOptionError:
                return ""
            except configparser.NoSectionError:
                return ""
        def get_float(self, block, name):
            """
            Get a float value from the configuration pareser

            :param block:
            :param name:
            :return: a float value from the configuration parser or 0.0 as default value.
            """
            str_value = self.get_string(block, name)
            try:
                return float(str_value)
            except:
                return 0.0
        def get_interger(self, block, name):
            """

            :param block:
            :param name:
            :return: an integer value from the configuration parser or 0 as default value.
            """
            str_value = self.get_string(block, name)
            try:
                return int(str_value)
            except:
                return 0

        def get_list(self, block, name):
            try:
                v = self.config.get(block, name)
                return set(json.loads(v))
            except:
                return set()


    def __new__(cls, filename=None):
        """
        Implementation of th singleton method.
        :param filename:
        """
        if ConfigTranslator.instance is None:
            ConfigTranslator.instance = ConfigTranslator.__ConfigTranslator(filename)
        return ConfigTranslator.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)


if __name__ == "__main__":
    tr = ConfigTranslator("config.cfg")
    l = tr.get_list("default", "context")
    print(l)
    print(type(l))

