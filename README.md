# RDF to NGSI-LD Translator

This Python project implements a generic translator from RDF to NGSI-LD.

The work takes inspiration from[rdflib](https://rdflib.readthedocs.io/en/stable/index.html) plugins that store RDF data in backends like Neo4j (https://github.com/neo4j-labs/rdflib-neo4j).

In this sense, this project provides an rdflib plugin where an NGSI-LD Context Broker works as the storage backend for RDF data. Additionally, the translator supports the ingestion of streams of RDF data via Kafka.

## Translation Rules

The following set of rules are applied to translate the RDF data model (triples) into the NGSI-LD data model (property graph):

- **Subject**:
  - Subjects represented by IRIs map directly to an NGSI-LD Entities. The URI of the subject in the RDF triple is the URI of the NGSI-LD Entity.

  > :warning: WARNING: This approach does not follow the convention recommended by ETSI CIM, which goes "urn:ngsi-ld:\<entity-type>:\<identifier>". The reason for doing this is to facilitate interoperability between RDF and NGSI-LD.

  - `Blank nodes` (or `BNodes`) are skolemized as described in Section 3.5 of [RDF 1.1 Concepts and Abstract Syntax](https://www.w3.org/TR/rdf11-concepts/#section-blank-nodes).
    By generating Skolem IRIs, blank nodes of an RDF graph can be transformed into NGSI-LD
    Entities and stored in the NGSI-LD Context Broker.

- **Predicate**:
  - **RDF classes**
    - `a` or `rdf:type` predicate maps to the NGSI-LD Entity Type. For example:
    the RDF triple `<http://example.org/people/Bob> a foaf:Person` translates into an NGSI-LD Entity of `foaf:Person` type, and URI `http://example.org/people/Bob`.

    - If no `rdf:type` predicate is found for the subject in the RDF graph, then the Entity Type will be set to `http://www.w3.org/2000/01/rdf-schema#Class` by default. As described in Section 2.2 of [RDF Schema 1.1](https://www.w3.org/TR/rdf-schema/#ch_class), the `rdfs:Class` represent the class of RDF classes.

  - **RDF Datatype property** maps to an NGSI-LD Property. A special treatment is required when the literal of the predicate uses `xsd:datetime`. In this case the resulting NGSI-LD Property must follow the special format:

    ```json
        "myProperty": {
            "type": "Property", "value": {
                "@type": "DateTime",
                "@value": "2018-12-04T12:00:00Z"
            }
        }
    ```

  - **RDF Object property** maps to an NGSI-LD Relationship. The target of the Relationship is the URI of the object in the RDF triple.

- **Namespaces**: There is no need to create specific `@context` for translating to NGSI-LD. The resulting NGSI-LD Entity can just used expanded the URIs. This approach is easier to maintain as avoids maintaining `@context` files.

  Optionally, If the ingested RDF data includes a definition of namespaces with prefixes, then this information could be used to generate the `@context` for the translated NGSI-LD Entity. The resulting `@context` can be send along the NGSI-LD payload or stored elsewhere and reference via Link header. The selected approach will depend on the use case and the developer's implementation.

## Translation Modes

The translator could be configured to expect `batches` of RDF data, instead of `streaming` 
events. In batching mode, the translator can analyze all RDF triples for the same subject, 
bundle the datatype and object properties, and

```
python main.py --to-kafka-demo tests/examples/simple-sample-relationship.ttl tests/examples/containerlab-graph.nt
```

produce a complete NGSI-LD Entity with a set of Properties and Relationships.
This approach can improve performance as less NGSI-LD requests are sent
to create the Entities in the Context Broker.

## Installation
### Prerequisites
Python 3.10+ is required. Some programming constructs from Python 3.10 has been used in the project. At least Python 3.11 is recommended.

### Installation in our system, with virtual environment
Creating a Python Virtual Environment is quite recommendable `virtualenv ~/.venv/rdf2ngsild` and activating the virtual environment before doing anything with `source ~/.ven/rdf2ngsild/bin/activate`. Then we can proceed with installation:

```
git clone https://gitlab.aeros-project.eu/wp4/t4.2/rdf-to-ngsi-ld.git
cd rdf-to-ngsi-ld
pip install -r requirements.txt
```

### Docker installation
The Docker image can be built using the following command:

```bash
sudo docker image build -t aeros-project/rdf-to-ngsi-ld:latest .
```

## Usage
The application reads RDF triples from a Kafka topic and converts them to NGSI-LD, writing the output to an NGSI-LD Context Broker (like Orion-LD): 

```bash
python main.py --from-kafka --to-ngsild-broker
```

## Configuration file
This is an example of a configuration file:

```ini
# Default configurations
[default]
## A list for the context - Just formatted like an array. This is to set the default context
context = ["https://fiware.github.io/data-models/context.jsonld"]

## context = ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"]

# Transformations to URN (as ETSI recommends.)
[urn-transform]
##
## This refers as how the "id" property of the entity is calculated_
##
## urn = std_urn_name - If this is the value, the id of the enties will be calculated from
##                      the URI value of RDF's file, something similar to this:
##                      id = urn:xxx:typeentity:identity
## Any other value will not transform anything
urn = std_urn_name_no

[type-transform]
##
## This refers as how the "type" property of the entity is calculated
##
## urn = std_type_name - If this is the value, the type will be calculated removing anything
##                       before the last ":" character. It can be other things and the name
##                       will be left as URI.
## urn = std_default_type - Sets default value according to parameter default_type_value
##
## urn = std_type_default
urn = std_type_default

retype_function = std_name_only
default_type_value = rdfs:resource

[predicates]
## format=long  -- Then a complete URL (if available) will be used for the properties of the 
##                            entities
## format=prefix -- If the type exists as <prefix>:<name> this will be used to be set in the
##                            entities
## format=""       -- Or any value, then only a short name will be used.
##
format=""

[encode-transform]
# This is only used when data is written on stdout. To help user to watch the URL in the
# context broker of the new entity.
#
# Encode or not encode the ID of the of the entity (used mainly for patches) -- If we use a
# URL as ID for the entity in Orion-ld, we need to encode it in order to put the ID in
# the URL as a paramter for the query.
#
# If the encoder here is as shown, then the encoder will encode the ID
# encoder = encode_url_as_http
#
# If we don't need to encode, we can use (this is the default behaviour):
# encoder = encode_url_not
# 
# If unquote, then the URIs are decoded to values.
# unquote = True | False 

encoder = encode_url_as_http

unquote = True

[kafka-client]
## Cofiguration for the Kafka reader. It will connect to a topic in a server
## It is used when the southbound is Kafka / RedPanda
servers = localhost:19092
topic = rdf-topic

# Timeout of reader. -1 means infinite.
reader_timeout = -1

[brokerld]
### NGSI-LD Broker basic URL to connect to when data is sent to NGSI-LD Broker.
## Used only when the northbound is ngsi-ld broker.
##
## url -- is the URL where the NGIS-LD Broker is waiting for connections
## pool_size -- The number of processes used to dispatch data to the NGSI-LD Broker
##              Test must be done for fine tuning, but too low and too high values doesn't get
##              the best performance out of the transformer
## concat_array -- If its value is True, it will use header 'aerOS-Array-Concat' in order
##                 to concat arrays in Orionld broker
url = http://localhost:1026
pool_size = 1
concat_array = False


[kafka-demo]
## This is for testing purposes. It is used with the --to-kafka parameter and it will
## say how many messages are going to be sent, and the waiting time between them.

## Max number of messages to be sent (<0 means infinity)
max_messages_sent = 10000

## thread.sleep between messages. It will send a message every... seconds
wait_between_messages = 0

[treat-as-array]
### Treat a set of attributes as an array
### 
### We define a list of attributes (URIs) that will be treated always as arrays.
###
attributes = [
"http://tmp1",
"http://tmp2"
]
```

## Testing purposes.

### Using Kafka / Red Panda
The idea of writing this translator started from the need to read RDF data from a queue, 
transforming it to NGSI-LD and writing that result to a NGSI-LD Context broker. So, this example 
will cover how to test this.

#### Feeding the Queue (preparing the test)
For testing purposes, the application can write data to a Kafka queue topic. This is the part of 
the configuration needed to write data to a kafka queue:
```ini
[kafka-client]
## Cofiguration for the Kafka reader. It will connect to a topic in a server
## It is used when the southbound is Kafka / RedPanda
servers = localhost:19092
topic = rdf-topic

# Timeout of reader. -1 means infinite.
reader_timeout = -1

[kafka-demo]
## This is for testing purposes. It is used with the --to-kafka parameter and it will
## say how many messages are going to be sent, and the waiting time between them.

## Max number of messages to be sent (<0 means infinity). In this case, we'll write 10000 messages
## in the queue
max_messages_sent = 10000

## thread.sleep between messages. It will send a message every... seconds
wait_between_messages = 0
```

And we can execute the following command:
```bash
python main.py --feed-kafka-demo tests/examples/simple-sample-relationship.ttl 
tests/examples/containerlab-graph.nt
```

The translator will insert in the kafka queue defined in the `ini` file behind `[kafka-client]
`the corresponding values.

#### Reading that data / benchmarking
We can configure the **translator** to read from the Kafka queue (where we previously inserted 
that data) and, let's say we can send that a NGSI-LD Broker listening on port 1026. We want to 
know how long did it take to read all the messages from the queue and write them in the Broker.

The relevant part of the `ini` file will be:

```ini
[brokerld]
### NGSI-LD Broker basic URL to connect to when data is sent to NGSI-LD Broker.
## Used only when the northbound is ngsi-ld broker.
## 
## url -- is the URL where the NGIS-LD Broker is waiting for connections
## pool_size -- The number of processes used to dispatch data to the NGSI-LD Broker
##              Test must be done for fine tuning, but too low and too high values doesn't get
##              the best performance out of the transformer. This only works if the transformer
##              is started with --async-run
## concat_array -- If its value is True, it will use header 'aerOS-Array-Concat' in order
##                 to concat arrays in Orionld broker
url = http://localhost:1026
pool_size = 1
concat_array = False

[kafka-client]
## Cofiguration for the Kafka reader. It will connect to a topic in a server
## It is used when the southbound is Kafka / RedPanda
servers = localhost:19092
topic = rdf-topic

# Timeout of reader. -1 means infinite.
reader_timeout = -1

[kafka-demo]
## This is for testing purposes. It is used with the --to-kafka parameter and it will
## say how many messages are going to be sent, and the waiting time between them.

## Max number of messages to be sent (<0 means infinity). In this case, we'll write 10000 messages
## in the queue
max_messages_sent = 10000

## thread.sleep between messages. It will send a message every... seconds
wait_between_messages = 0
```

So, in order to perform the benchmarking we could run the transformer:

```
❯ ./main.py  --async-run --from-kafka --to-ngsild-broker --benchmark

TIME: 7.603782892227173
```

It took 7.6 seconds to read 10000 (as show in `max_messages_sent`) and writing them to a broker. 
This roughly means 1315 messages per second.

If we don't run that with several cores:

```
❯ ./main.py  --from-kafka --to-ngsild-broker --benchmark

TIME: 143.14611268043518
```

It is much slower, less than 70 messages per second.


## Meaning of the "transformations"
Let's use as a simple RDF for the examples the following RDF file:

```rdf
@prefix aeros: <https://w3id.org/aerOS/continuum#> .
@prefix aerdcat: <https://w3id.org/aerOS/data-catalog#> .
@prefix a4bdg: <https://w3id.org/aerOS/building#> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix ex: <https://example.org/> .
@prefix org: <http://www.w3.org/ns/org#> .
@base <https://example.org/> .
# From here on... errors because these were not added.

@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix seas: <https://w3id.org/seas/>.  # Smart Energy Aware Systems
@prefix bot:  <https://w3id.org/bot#> .  # Building Topology Ontology
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

ex:DP101 a aerdcat:DataProduct ;
    dcterms:identifier "Data Product 101" ;
    dcterms:description "Contains data related to the inventory of desks" ;
    dcat:keyword "network lab DEVNET",
                 "Marousi" ;
    dcat:theme a4bdg:Desk ;
    aerdcat:mapping ex:TM101 ;
    dcterms:publisher ex:UserAAA ;
    dcat:distribution ex:Dist101 .
```

In every of the following examples I'll change the config file but I'll execute the very same 
command:
```bash
./main.py --print tests/examples/simple-sample-test-expansions.ttl | jq .
```
### The `ìd` property: `urn_transform` section in config file
This parameter only affects the `id` property of the entity

#### Get the very long name (an url)
```ini
[urn-transform]
urn = std_urn_name_no
```

The output will be (piped to `jq '{ "id": .id}'`)
```json
{
  "id": "https://example.org/DP101"
}
```

This also affects the **Relationships**, for example
```json lines
....
  "distribution": {
    "type": "Relationship",
    "object": "https://example.org/Dist101"
  },
....
```
#### Get urn as suggested by ETSI
```ini
[urn-transform]
urn = std_urn_name
```
The output will be (piped to `jq '{ "id": .id}'`)
```json
{
  "id": "urn:ngsi-ld:DP101"
}
```

And of course, in Relationship lines:
```json lines
....
   "distribution": {
      "type": "Relationship",
      "object": "urn:ngsi-ld:Dist101"
   },
....
```

### The `type` property: `type_transform` section in config file
There is a default value when the `type` can't be deducted from the RDF file. All data which 
type is unknown will be set to the value set in the `default_type_value`.

So, the interesting variables are `urn` and `retype_function`.
```ini
[type-transform]
urn = std_type_default
retype_function = std_name_only

# Use expanded URI for rdfs:Class by default, and compress if @context is provided
default_type_value = http://www.w3.org/2000/01/rdf-schema#Class
```

#### Get the simples name for `type`
```ini
[type-transform]
retype_function = std_name_only
```

The `type` property will be shown as:
```json
{
  "type": "DataProduct"
}
```

#### Get the `type` as etsi-urn
```ini
[type-transform]
retype_function = std_urn_name
```

The `type` property will be shown as:
```json
{
    "type": "urn:ngsi-ld:data-catalog:DataProduct"
}
```

#### Get the `type` as default type (possibly url)
```ini
[type-transform]
retype_function = std_default_type
```

The `type` property will be shown as:
```json
{
    "type": "https://w3id.org/aerOS/data-catalog#DataProduct"
}
```

### Get property names
The property names could be a long name (URL), an abbreviated name (rdfs:whatever) or a very 
short name.

```ini
[predicates]
## format=long  -- Then a complete URL (if available) will be used for the properties of the 
##                            entities
## format=prefix -- If the type exists as <prefix>:<name> this will be used to be set in the
##                            entities
## format=""       -- Or any value, then only a short name will be used.
##
format=""
```

We can have 3 possible values for a property. Let's consider the property `description`, it can 
take one of the 3 names:

* `description`  if `format = ""`
* `dcterms:description`  if `format = prefix`
* `http://purl.org/dc/terms/description` if `format = long`

## Attributtes defined as arrays
In order to define an attribute as an array, in the config file we must define a section like the following
one:

```ini
[treat-as-array]
### Treat a set of attributes as an array
### 
### We define a list of attributes (URIs) that will be treated always as arrays.
###
attributes = [
"http://tmp1",
"http://tmp2"
]
```

So, when the conversor meets any of those attributes, it will treat them as an array instead of a single
attribute.