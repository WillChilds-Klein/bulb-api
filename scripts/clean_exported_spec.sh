#!/bin/bash

set -ex

spec="${1:-"./api/spec/swagger.yaml"}"

# clean up operation id's
sed -i 's/GET\-/api.handlers.get_/' $spec
sed -i 's/LIST\-/api.handlers.list_/' $spec
sed -i 's/POST\-/api.handlers.create_/' $spec
sed -i 's/PUT\-/api.handlers.update_/' $spec
sed -i 's/DELETE\-/api.handlers.delete_/' $spec

# clean up empty defaults
sed -i "/default: ''/d" $spec
