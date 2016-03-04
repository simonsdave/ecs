#!/usr/bin/env bash
#
# this script is a wrapper around nginx
#

if [ "-v" == "${1:-}" ]; then
    VERBOSE=1
    shift
else
    VERBOSE=0
fi

if [ $# != 2 ]; then
    echo "usage: `basename $0` [-v] <api-docs-domain-name> <api-domain-name>" >&2
    exit 1
fi

API_DOCS_DOMAIN_NAME=${1:-}
API_DOMAIN_NAME=${2:-}

cat /etc/nginx/sites-available/default.template | \
    sed -e "s|%API_DOCS_DOMAIN_NAME%|$API_DOCS_DOMAIN_NAME|g" | \
    sed -e "s|%API_DOMAIN_NAME%|$API_DOMAIN_NAME|g" > \
    /etc/nginx/sites-available/default

#
# configuration is good to go! time to start nginx:-)
#
nginx

exit 0
