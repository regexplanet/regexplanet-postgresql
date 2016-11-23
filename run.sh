#!/bin/bash

#/usr/local/google_appengine/dev_appserver.py --port=8081 .
export $(cat local.env)
python regexplanet-api.py
