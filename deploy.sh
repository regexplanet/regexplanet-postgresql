#!/bin/bash
#
# deploy the xregexp backend to zeit
#

heroku container:push --app regexplanet-postgresql web


#echo "INFO: listing existing versions"
#now ls regexplanet-postgresql

#echo "INFO: deploying"
#now && now alias

#
# need to kill the old version!
#
#echo "INFO: removing the old version "
#echo "WARNING: must be done manually with 'now rm'"
