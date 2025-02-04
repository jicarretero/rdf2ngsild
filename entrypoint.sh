#!/bin/bash

# aerOS - RDF to NGSI-LD Translator
# author: José Ignacio Carretero Guarde <joseignacio.carretero@fiware.org>

PROJECT=aeros
COMPONENT=rdf-to-ngsild
INSTALLATION_PATH=/opt/$PROJECT/$COMPONENT

# Start the first process
cd $INSTALLATION_PATH
# maybe we could need arguments... export $(cat .env | xargs)
python3 main.py --from-kafka --to-ngsild-broker &

# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?
