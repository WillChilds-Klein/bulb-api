#!/bin/bash

set -ex

spec="${1:-"spec/swagger.yaml"}"

# clean up operation id's
sed -i 's/GET\-/app.get_/' $spec
sed -i 's/LIST\-/app.list_/' $spec
sed -i 's/POST\-/app.create_/' $spec
sed -i 's/PUT\-/app.update_/' $spec
sed -i 's/DELETE\-/app.delete_/' $spec

# clean up empty defaults
sed -i "/default: ''/d" $spec
