#!/bin/bash

set -ex

spec="${1:-"./bulb_api/spec/swagger.yaml"}"

# clean up operation id's
sed -i 's/GET\-/bulb_api.handlers.get_/' $spec
sed -i 's/LIST\-/bulb_api.handlers.list_/' $spec
sed -i 's/POST\-/bulb_api.handlers.create_/' $spec
sed -i 's/PUT\-/bulb_api.handlers.update_/' $spec
sed -i 's/DELETE\-/bulb_api.handlers.delete_/' $spec

# clean up empty defaults
sed -i "/default: ''/d" $spec
