# aerOS - Conversor
# author: joseignacio.carretero <joseignacio.carretero@fiware.org>

# Stage GIT CLONE
FROM alpine/git AS git-clone

ARG PROJECT=aeros
ARG COMPONENT=rdf-to-ngsild
ARG VERSION=main
ARG INSTALLATION_PATH=/opt/$PROJECT/$COMPONENT

RUN mkdir -p $INSTALLATION_PATH

# https://gitlab.aeros-project.eu/wp4/t4.2/rdf-to-ngsi-ld.git
RUN git clone https://github.com/jicarretero/rdf2ngsild.git --branch $VERSION $INSTALLATION_PATH


# Stage PIP REQUIREMENTS
FROM python:3.11-alpine AS pip-requirements

ARG PROJECT=aeros
ARG COMPONENT=rdf-to-ngsild
ARG VERSION=main
ARG INSTALLATION_PATH=/opt/$PROJECT/$COMPONENT

RUN apk add --no-cache --virtual .build-deps gcc musl-dev linux-headers libffi-dev cargo openssl-dev

RUN mkdir -p $INSTALLATION_PATH
COPY --from=git-clone $INSTALLATION_PATH/requirements.txt /requirements.txt
RUN pip install --prefix=$INSTALLATION_PATH -r /requirements.txt && chmod +x $INSTALLATION_PATH/main.py || true

# Stage FINAL
# FROM python:3.11-bookworm as final
FROM python:3.11-alpine AS final

ARG PROJECT=aeros
ARG COMPONENT=rdf-to-ngsild
ARG VERSION=main
ARG INSTALLATION_PATH=/opt/$PROJECT/$COMPONENT

LABEL maintainer="joseignacio.carretero@fiware.org"
LABEL description="rdf to ngsi-ld component built with Python version 3.11 on Debian bookworm Linux"
LABEL version=$VERSION

RUN mkdir -p $INSTALLATION_PATH

COPY --from=git-clone $INSTALLATION_PATH $INSTALLATION_PATH
COPY --from=pip-requirements $INSTALLATION_PATH /usr/local

# COPY settings/$VERSION/config.ini $INSTALLATION_PATH/
# COPY settings/$VERSION/.env $INSTALLATION_PATH/


WORKDIR ${INSTALLATION_PATH}
# python main.py --from-kafka --to-orionld
ENTRYPOINT [ "./main.py", "--from-kafka", "--to-ngsild-broker", "--async-run" ]
