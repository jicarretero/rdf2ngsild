# GUARD - LCP
# author: Alex Carrega <alessandro.carrega@cnit.it>

# Stage GIT CLONE
FROM alpine/git as git-clone

ARG PROJECT=aeros
ARG COMPONENT=rdf-to-ngsild
ARG VERSION=main
ARG INSTALLATION_PATH=/opt/$PROJECT/$COMPONENT

RUN mkdir -p $INSTALLATION_PATH

# https://gitlab.aeros-project.eu/wp4/t4.2/rdf-to-ngsi-ld.git
RUN git clone https://github.com/jicarretero/rdf2ngsild.git --branch $VERSION $INSTALLATION_PATH


# Stage PIP REQUIREMENTS
FROM python:3.11-alpine as pip-requirements

ARG PROJECT=aeros
ARG COMPONENT=rdf-to-ngsild
ARG VERSION=develop
ARG INSTALLATION_PATH=/opt/$PROJECT/$COMPONENT

RUN apk add --no-cache --virtual .build-deps gcc musl-dev linux-headers

RUN mkdir -p $INSTALLATION_PATH
COPY --from=git-clone $INSTALLATION_PATH/requirements.txt /requirements.txt
RUN pip install --prefix=$INSTALLATION_PATH -r /requirements.txt


# Stage FINAL
FROM python:3.11-bookworm as final

ARG PROJECT=aeros
ARG COMPONENT=rdf-to-ngsild
ARG VERSION=develop
ARG INSTALLATION_PATH=/opt/$PROJECT/$COMPONENT

LABEL maintainer="joseignacio.carretero@fiware.org"
LABEL description="rdf to ngsi-ld component built with Python version 3.11 on Debian bookworm Linux"
LABEL version=$VERSION

RUN mkdir -p $INSTALLATION_PATH

COPY --from=git-clone $INSTALLATION_PATH $INSTALLATION_PATH
COPY --from=pip-requirements $INSTALLATION_PATH /usr/local

# COPY settings/$VERSION/config.ini $INSTALLATION_PATH/
# COPY settings/$VERSION/.env $INSTALLATION_PATH/

RUN mv $INSTALLATION_PATH/entrypoint.sh / && chmod +x entrypoint.sh

# python main.py --from-kafka --to-orionld
ENTRYPOINT [ "/entrypoint.sh" ]
