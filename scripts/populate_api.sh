#!/bin/bash

usage() { echo "Usage: $0 [--test] "1>&2; exit ${1:-"0"}; }

TEST_API=
VERBOSE=
while [[ $# -gt 0 ]]; do
    case "$1" in
        -t|--test)
            TEST_API=1
            ;;
        -h|--help)
            usage 0
            ;;
        -v)
            VERBOSE=1
            ;;
        *)
            break
            ;;
    esac
    shift
done

# fail on any command error
set -e

# print all commands run to terminal if verbosity is requested
if [[ -n "$VERBOSE" ]]; then
    set -x
fi

# install httpie if not installed
which http &>/dev/null \
    || pip install http

# where to serve from?
BASE_URL=${1:-"http://localhost:8080"}

do_post() {
    local endpoint="$1"
    local json="$2"
    echo $json \
    | http --check-status POST "$BASE_URL/$(basename $endpoint)" \
        'Authorization: Bearer master_key'
}

do_list() {
    local endpoint="$1"
    http --check-status GET "$BASE_URL/$(basename $endpoint)" \
        'Authorization: Bearer master_key'
}

# TODO: modify this script to use test data JSON files...

# populate documents
do_post /documents '{"name": "taxes", "org_id": "1", "uri": "https://bulb-documents.s3.amazonaws.com/this_documents_uuid", "status": "IN_PROGRESS"}'
do_post /documents '{"name": "wages", "org_id": "2", "uri": "https://bulb-documents.s3.amazonaws.com/this_documents_uuid", "status": "NOT_STARTED"}'

# populate organizations
do_post /organizations '{"name": "mass chicken", "users": ["1"], "type": "BUYER"}'
do_post /organizations '{"name": "ginos pizza", "users": ["2","3"], "type": "BUYER"}'
do_post /organizations '{"name": "local foods ltd.", "users": ["8","9"], "type": "VENDOR"}'

# populate resources
do_post /resources '{"name": "Shitty Services", "s3_thumbnail_uri": "https://yourmom.s3.amazonaws.com/foo.png",
                     "url": "http://www.shittyservices.net", "mailto_uri": "mailto:person@shittyservices.net"}'
do_post /resources '{"name": "MA SBA", "s3_thumbnail_uri": "https://yourmom.s3.amazonaws.com/sba.png",
                     "url": "http://www.sba.gov", "mailto_uri": "mailto:govt_drone_69@sba.gov"}'

# populate users
do_post /users '{"name": "harold", "email": "harry@balls.com", "password": "password"}'
do_post /users '{"name": "gino", "email": "gino@greasypizza.com", "password": "password"}'
do_post /users '{"name": "gina", "email": "gina@greasypizza.com", "password": "password"}'

# populate tasks
#do_post /tasks '{"org_id": "c51d7bd8-61ce-11e7-9210-ebdb9a35a3dc", "name": "create business plan", "priority": 0.0, "status": "NOT_STARTED", "workspaces": ["FORMATION"], "url": "https://static.bulb.co/formation/business_plan"}'
#do_post /tasks '{"org_id": "c51d7bd8-61ce-11e7-9210-ebdb9a35a3dc", "name": "file taxes", "priority": 0.82, "status": "NOT_STARTED", "workspaces": ["TAX"], "url": "https://bulb.co/tax/filing_taxes"}'
#do_post /tasks '{"org_id": "2f4e6ddc-61cf-11e7-909b-530d5d6b74b5", "name": "create business plan", "priority": 0.0, "status": "NOT_STARTED", "workspaces": ["FORMATION"], "url": "https://static.bulb.co/formation/business_plan"}'
#do_post /tasks '{"org_id": "2f4e6ddc-61cf-11e7-909b-530d5d6b74b5", "name": "file taxes", "priority": 0.82, "status": "NOT_STARTED", "workspaces": ["TAX"], "url": "https://bulb.co/tax/filing_taxes"}'


# now do a quick test to make sure we're returning the proper values
if [[ -n $TEST_API ]]; then
    do_list /documents
    do_list /organizations
    do_list /resources
    do_list /users
fi
