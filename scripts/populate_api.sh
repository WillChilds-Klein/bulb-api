#!/bin/bash

set -ex

which http || pip install http

base_url=${1:-"http://localhost:8080"}

# populate users
echo '{"id": "1", "name": "harold", "email": "harry@balls.com", "organizations": ["1"]}' | \
    http POST $base_url/users
echo '{"id": "2", "name": "gino", "email": "gino@greasypizza.com", "organizations": ["2"]}' | \
    http POST $base_url/users
echo '{"id": "3", "name": "gina", "email": "gina@greasypizza.com", "organizations": ["2"]}' | \
    http POST $base_url/users

# populate organizations
echo '{"id": "1", "name": "mass chicken", "users": [1]}' \
    | http POST $base_url/organizations
echo '{"id": "2", "name": "ginos pizza", "users": [2,3]}' \
    | http POST $base_url/organizations

# populate documents
echo '{"id": "1", "name": "taxes", "organization": "1"}' \
    | http POST $base_url/documents
