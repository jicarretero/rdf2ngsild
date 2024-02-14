import configparser

class ConfigTranslator:
    instance = None

    class __ConfigTranslator:
        def __init__(self, filename):
            self.config = configparser.ConfigParser()
            self.filename = filename
            self.config.read(filename)

        def get_string(self, block, name):
            try:
                return self.config.get(block, name)
            except configparser.NoOptionError:
                return ""
            except configparser.NoSectionError:
                return ""
        def get_float(self, block, name):
            str_value = self.get_string(block, name)
            try:
                return float(str_value)
            except:
                return 0.0
        def get_interger(self, block, name):
            str_value = self.get_string(block, name)
            try:
                return int(str_value)
            except:
                return 0


    def __new__(cls, filename=None):
        if ConfigTranslator.instance is None:
            ConfigTranslator.instance = ConfigTranslator.__ConfigTranslator(filename)
        return ConfigTranslator.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

