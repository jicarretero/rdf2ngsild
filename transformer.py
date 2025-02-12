from config_translator import ConfigTranslator
import functools
from urllib.parse import unquote as urllib_unquote

def std_name_only(data: str) -> str:
    """
    Transform a subject to its name only, example -

    Given "https://whatever.url/somedirectory/somesubdirectory#the_name
    Returns "the_name"

    :param data:
    :return:
    """
    return data[data.find("#")+1:]


def std_urn_name(data: str) -> str:
    """
    Transform a subject to some calculated URN, example -

    Given "https://whatever.url/somedirectory/somesubdirectory#the_name
    Returns "urn:ngsi-ld:somesubdirectory:the_name"

    :param data:
    :return:
    """
    import os.path
    new_id = "urn:ngsi-ld:" + os.path.basename(data).replace("#", ":")
    return new_id


def std_type_default(data: str) -> str:
    ct = ConfigTranslator.instance
    default_value = ct.get_string("type-transform", "default_type_value")
    if default_value == "":
        raise KeyError
    return default_value


def std_type_name(data: str) -> str:
    import os.path
    return os.path.basename(data).replace("#", "")


@functools.cache
def global_transformer(f_name: str, data: str) -> str:
    """
    Transforms the name into some value, depending on the function to be used (the function name is the 1st parameter).
    If nothing valid is there, the same data is returned. This name can be configured in the configuration file.

    :param f_name:
    :param data:
    :return:
    """
    if f_name == "":
        return data

    try:
        f = globals()[f_name]
        return f(data)
    except KeyError:
        return data


def transformer(data: str) -> str:
    ct = ConfigTranslator.instance
    f_name = ct.get_string("urn-transform", "urn")
    return global_transformer(f_name, data)


def type_transformer(data: str) -> str:
    ct = ConfigTranslator.instance
    f_name = ct.get_string("type-transform", "urn")
    return global_transformer(f_name, data)

def retype(data: str, reason: str, default_type: str) -> str:
    ct = ConfigTranslator.instance
    f_name = ct.get_string("type-transform", "retype_function")
    if reason == 'a':
        return global_transformer(f_name, data)
    return default_type

def encode_url_as_http(uri_string: str) -> str:
    """
    This function will provide an URL properly encoded to be sent as a paramater in the HTTP repests.

    :param uri_string:
    :return:
    """
    result = ''
    accepted = [c for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456787-._~'.encode('utf-8')]
    for char in uri_string.encode('utf-8'):
        result += chr(char) if char in accepted else '%{}'.format(hex(char)[2:]).upper()
    return result



def encode_url_not(uri_string: str) -> str:
    """
    Does not encode the url according to
    :param uri_string:
    :return:
    """
    return uri_string

def encode_url(data: str) -> str:
    """
    Encodes an url according to standard transformation.

    :param data:
    :return:
    """
    ct = ConfigTranslator.instance
    f_name = ct.get_string("encode-transform", "encoder")
    return global_transformer(f_name, data)

def unquote(data: str) -> str:
    """
    Decodes URIs if unquote is True.

    :param data:
    :return:
    """
    d = data
    ct = ConfigTranslator.instance
    if ct.get_boolean("encode-transform", "unquote"):
        d = urllib_unquote(data)
    return d

if __name__ == "__main__":
    print(encode_url_as_http("http://www.w3.org/ns/org"))
