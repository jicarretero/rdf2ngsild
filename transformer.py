from config_translator import ConfigTranslator


def std_name_only(data: str) -> str:
    return data[data.find("#")+1:]
def std_urn_name(data: str) -> str:
    import os.path
    return "urn:ngsi-ld:" + os.path.basename(data).replace("#", ":")


def std_type_name(data: str) -> str:
    import os.path
    return os.path.basename(data).replace("#","")


def global_transformer(f_name: str, data: str) -> str:
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


if __name__ == "__main__":
    print(std_name_only("http://candil.namespace.com#clab-srlinux-openconfig-02-srl2"))