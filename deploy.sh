#!/bin/bash
#
# deploy the postgresql backend to heroku
#

set -o errexit
set -o pipefail
set -o nounset

heroku config:set --app regexplanet-postgresql COMMIT=$(git rev-parse --short HEAD)  LASTMOD=$(date -u +%Y-%m-%dT%H:%M:%SZ)

heroku container:push --app regexplanet-postgresql web
heroku container:release --app regexplanet-postgresql web

