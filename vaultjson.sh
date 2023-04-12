#!/bin/bash
# This script converts the capem.pem and cakey.pem into ca.json for Vault upload
first=`echo '{ "pem_bundle": "'`
second=`awk '{printf "%s\\\n", $0}' ssl/private/cakey.pem ssl/cacert.pem`
third=`echo '" }'`
total="${first}${second}${third}"
echo "${total}" > ca.json
