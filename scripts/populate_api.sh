#!/bin/bash

set -ex

which http || pip install http

base_url=${1:-"http://localhost:8080"}

do_post() {
    local endpoint="$1"
    local json="$2"
    echo $json | \
        http --check-status POST "$base_url/$(basename $endpoint)"
}

# populate users
do_post /users '{"name": "harold", "email": "harry@balls.com", "organizations": ["1"]}'
do_post /users '{"name": "gino", "email": "gino@greasypizza.com", "organizations": ["2"]}'
do_post /users '{"name": "gina", "email": "gina@greasypizza.com", "organizations": ["2"]}'

# populate organizations
do_post /organizations '{"name": "mass chicken", "users": ["1"]}'
do_post /organizations '{"name": "ginos pizza", "users": ["2","3"]}'

# populate documents
do_post /documents '{"name": "taxes", "organization": "1"}'
do_post /documents '{"name": "taxes", "organization": "1"}'

# populate resources
do_post /resources '{"name": "Shitty Services", "s3_thumbnail_uri": "https://yourmom.s3.amazonaws.com/foo.png", 
                     "url": "http://www.shittyservices.net", "mailto_uri": "mailto:person@shittyservices.net"}'
do_post /resources '{"name": "MA SBA", "s3_thumbnail_uri": "https://yourmom.s3.amazonaws.com/sba.png", 
                     "url": "http://www.sba.gov", "mailto_uri": "mailto:govt_drone_69@sba.gov"}'
