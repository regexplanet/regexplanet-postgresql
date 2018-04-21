#!/bin/bash
#
# server startup for regexplanet-postgresql
#

echo "INFO: started PostgreSQL..."
service postgresql start

/usr/bin/python --version

echo "INFO: starting python API server..."
/usr/bin/python regexplanet-api.py


