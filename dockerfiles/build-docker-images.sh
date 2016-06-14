#!/usr/bin/env bash
#
# This script builds all of ECS' docker images
#

set -e

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

VERBOSE=0
TAG=""

while true
do
    OPTION=`echo ${1:-} | awk '{print tolower($0)}'`
    case "$OPTION" in
        -v)
            shift
            VERBOSE=1
            ;;
        -t)
            shift
            TAG=${1:-}
            shift
            ;;
        *)
            break
            ;;
    esac
done

if [ $# != 3 ] && [ $# != 5 ]; then
    echo "usage: `basename $0` [-v] [-t <tag>] <services-tar-gz> <api-docs-tar> <username> [<email> <password>]" >&2
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
    -t "$TAG" \
    "$USERNAME" \
    "$EMAIL" \
    "$PASSWORD"

"$SCRIPT_DIR_NAME/apidocs/build-docker-image.sh" \
    -t "$TAG" \
    "$API_DOCS_TAR" \
    "$USERNAME" \
    "$EMAIL" \
    "$PASSWORD"

"$SCRIPT_DIR_NAME/services/build-docker-image.sh" \
    -t "$TAG" \
    "$SERVICES_TAR_GZ" \
    "$USERNAME" \
    "$EMAIL" \
    "$PASSWORD"

exit 0
