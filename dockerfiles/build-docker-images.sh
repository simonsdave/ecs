#!/usr/bin/env bash
#
# This script builds all of ECS' docker images
#

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

if [ "-v" == "${1:-}" ]; then
    VERBOSE=1
    shift
else
    VERBOSE=0
fi

if [ $# != 3 ] && [ $# != 5 ]; then
    echo "usage: `basename $0` [-v] <services-tar-gz> <api-docs-tar> <username> [<email> <password>]" >&2
    exit 1
fi

SERVICES_TAR_GZ=${1:-}
API_DOCS_TAR=${2:-}
USERNAME=${3:-}
EMAIL=${4:-}
PASSWORD=${5:-}

if [ ! -r "$SERVICES_TAR_GZ" ]; then
    echo "can't find source dist '$SERVICES_TAR_GZ'" >&2
    exit 1
fi

if [ ! -r "$API_DOCS_TAR" ]; then
    echo "can't find api docs tar file '$API_DOCS_TAR'" >&2
    exit 1
fi

"$SCRIPT_DIR_NAME/nginx/build-docker-image.sh" \
    "$USERNAME" \
    "$EMAIL" \
    "$PASSWORD"

"$SCRIPT_DIR_NAME/apidocs/build-docker-image.sh" \
    "$API_DOCS_TAR" \
    "$USERNAME" \
    "$EMAIL" \
    "$PASSWORD"

"$SCRIPT_DIR_NAME/services/build-docker-image.sh" \
    "$SERVICES_TAR_GZ" \
    "$USERNAME" \
    "$EMAIL" \
    "$PASSWORD"

exit 0
