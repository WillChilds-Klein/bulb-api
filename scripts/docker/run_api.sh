#!/usr/bin/env bash

usage() {
    local exit_code=${1:-"0"}
    echo "Usage: $0 [-d] [-i IMAGE] [-n NAME] [-p PORT] IMAGE [ARGS ...]" 1>&2
    if [ $exit_code = "0" ]; then
    echo "  -d          detach container from std{out,in}"
    echo "  -h          print this message and exit"
    echo "  -i IMAGE    which image/container to run"
    echo "  -n NAME     container's name"
    echo "  -p PORT     port to link to localhost"
    echo "              NOTE: must specify port to run.py manually"
    echo "  -v          verbose, enable -x"
    fi
    exit $exit_code
}

export_arg () {
    if [[ -z $1 ]] || [[ -z $2 ]]; then
        usage 1
    else
        export "$1"="$2"
    fi
}

DETACH=
IMAGE="lambda"
NAME="api"
PORT=8080
VERBOSE=
while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--detach)
            DETACH=1
            ;;
        -i|--image)
            export_arg IMAGE $2
            shift
            ;;
        -h|--help)
            usage 0
            ;;
        -n|--name)
            export_arg NAME $2
            shift
            ;;
        -p|--port)
            export_arg PORT $2
            shift
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
           $([[ -n $DETACH ]] && echo -n '-d ') \
           --name "$NAME" \
           -p ${PORT}:${PORT} \
           -v "$(pwd)":/var/bulb \
           -e AWS_ACCESS_KEY_ID="$(aws configure get aws_access_key_id)" \
           -e AWS_SECRET_ACCESS_KEY="$(aws configure get aws_secret_access_key)" \
           -e AWS_DEFUALT_REGION="$(aws configure get region)" \
           -e FLASK_DEBUG='1' \
    ${IMAGE} \
    $@
