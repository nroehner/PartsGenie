#!/usr/bin/env bash

# Docker compose up partsgenie container with optional PORT_NUMBER
# Args: [PORT_NUMBER]

PORT_NUMBER=$1
if [ -z "$PORT_NUMBER" ]
then
    PORT_NUMBER=5000
fi

# docker run -d -p $1:5000 partsgenie
PORT=$PORT_NUMBER docker-compose up -d

echo '''#
# To stop the server, use
#
#    $ docker-compose down
#'''