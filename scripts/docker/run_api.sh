#!/usr/bin/env bash

usage() {
    local exit_code=${1:-"0"}
    echo "Usage: $0 [-d] [-i IMAGE] [-n NAME] [-p PORT] IMAGE [ARGS ...]" 1>&2
    if [ $exit_code = "0" ]; then
    echo "  --auth-port localhost port for token validation"
    echo "  -d          detach container from std{out,in}"
    echo "  -h          print this message and exit"
    echo "  -i IMAGE    which image/container to run"
    echo "  -l CNTNR    link to another local container"
    echo "  --no-link   don't link any containers to this one"
    echo "  -n NAME     container's name"
    echo "  -p PORT     port to link to localhost"
    echo "  --prod      run without FLASK_DEBUG set"
    echo "              NOTE: must specify port to run.py manually"
    echo "  -v          verbose, enable -x"
    fi
    exit $exit_code
}

DETACH=
IMAGE="lambda"
LINK="ddb_local"
NAME="bulb_api"
PORT=8080
AUTH_PORT=9090
PROD=
VERBOSE=
while [[ $# -gt 0 ]]; do
    case "$1" in
        --auth-port)
            AUTH_PORT=$2
            shift
            ;;
        -d|--detach)
            DETACH=1
            ;;
        -h|--help)
            usage 0
            ;;
        -i|--image)
            IMAGE=$2
            shift
            ;;
        -l|--link)
            LINK=$2
            shift
            ;;
        --no-link)
            LINK=
            ;;
        -n|--name)
            NAME=$2
            shift
            ;;
        -p|--port)
            PORT=$2
            shift
            ;;
        --prod)
            PROD=1
            ;;
        -v|--verbose)
            VERBOSE=1
            ;;
        *)
            break
            ;;
    esac
    shift
done

if [[ -n $VERBOSE ]]; then
    set -x
fi

set -e

docker run --rm \
           $([[ -n $DETACH ]] && echo -n '-d ' || echo -n '-it') \
           $([[ -n $LINK ]] && echo -n "--link $LINK") \
           --name "$NAME" \
           -p ${PORT}:${PORT} \
           -v "$(pwd)":/var/bulb \
           -e AWS_ACCESS_KEY_ID="$(aws configure get aws_access_key_id)" \
           -e AWS_SECRET_ACCESS_KEY="$(aws configure get aws_secret_access_key)" \
           -e AWS_DEFAULT_REGION="$(aws configure get region)" \
           -e PYTHONDONTWRITEBYTECODE=1 \
           -e TOKENINFO_URL="http://localhost:${AUTH_PORT}/auth" \
           $([[ -z $PROD ]] && echo -n '-e FLASK_DEBUG=1') \
    ${IMAGE} \
    $@
