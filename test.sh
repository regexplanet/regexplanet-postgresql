#!/bin/bash
#
# test the API using curl
#
# to test in the browser:
# http://www.regexplanet.com/advanced/python/index.html?testurl=http://localhost:8080/test.json

curl --verbose "http://localhost:8080/test.json?regex=A(B*)&replacement=A$2&input=CCC&input=ABBB&input=AB&input=BAB&input=CCC&input=DDD"
