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

if [ $# != 6 ]; then
    echo "usage: `basename $0` [-v] <api-docs-domain-name> <api-domain-name> <api per ip conn limit> <api per ip rate limit> <api per key conn limit> <api per key rate limit>" >&2
    exit 1
fi

API_DOCS_DOMAIN_NAME=${1:-}
API_DOMAIN_NAME=${2:-}
API_PER_IP_CONN_LIMIT=${3:-}
API_PER_IP_RATE_LIMIT=${4:-}
API_PER_KEY_CONN_LIMIT=${5:-}
API_PER_KEY_RATE_LIMIT=${6:-}

cat /etc/nginx/conf.d/ecs.conf.template | \
    sed -e "s|%API_DOCS_DOMAIN_NAME%|$API_DOCS_DOMAIN_NAME|g" | \
    sed -e "s|%API_DOMAIN_NAME%|$API_DOMAIN_NAME|g" > \
    sed -e "s|%API_PER_IP_CONN_LIMIT%|$API_PER_IP_CONN_LIMIT|g" > \
    sed -e "s|%API_PER_IP_RATE_LIMIT%|$API_PER_IP_RATE_LIMIT|g" > \
    sed -e "s|%API_PER_KEY_CONN_LIMIT%|$API_PER_KEY_CONN_LIMIT|g" > \
    sed -e "s|%API_PER_KEY_RATE_LIMIT%|$API_PER_KEY_RATE_LIMIT|g" > \
    /etc/nginx/conf.d/ecs.conf

#
# configuration is good to go! time to start nginx:-)
#
nginx

exit 0
