#!/usr/bin/env bash
#
# This script builds all of ECS' docker images
#

set -e

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

VERBOSE_FLAG=""
TAG_FLAG=""

while true
do
    OPTION=`echo ${1:-} | awk '{print tolower($0)}'`
    case "$OPTION" in
        -v)
            shift
            VERBOSE_FLAG=-v
            ;;
        -t)
            shift
            # this script can be called by travis which may pass
            # a zero length tag argument and hence the need for
            # the if statement below
            if [ "${1:-}" != "" ]; then
                TAG_FLAG="-t ${1:-}"
            fi
            # the shift assumes the arg after the -t is always a
            # tag name it just might be a zero length tag name
            shift
            ;;
        *)
            break
            ;;
    esac
done

if [ $# != 3 ] && [ $# != 4 ]; then
    echo "usage: `basename $0` [-v] [-t <tag>] <services-tar-gz> <api-docs-tar> <username> [<password>]" >&2
    exit 1
fi

SERVICES_TAR_GZ=${1:-}
API_DOCS_TAR=${2:-}
USERNAME=${3:-}
PASSWORD=${4:-}

if [ ! -r "$SERVICES_TAR_GZ" ]; then
    echo "can't find source dist '$SERVICES_TAR_GZ'" >&2
    exit 1
fi

if [ ! -r "$API_DOCS_TAR" ]; then
    echo "can't find api docs tar file '$API_DOCS_TAR'" >&2
    exit 1
fi

"$SCRIPT_DIR_NAME/nginx/build-docker-image.sh" \
    $VERBOSE_FLAG \
    $TAG_FLAG \
    "$USERNAME" \
    "$PASSWORD"

"$SCRIPT_DIR_NAME/apidocs/build-docker-image.sh" \
    $VERBOSE_FLAG \
    $TAG_FLAG \
    "$API_DOCS_TAR" \
    "$USERNAME" \
    "$PASSWORD"

"$SCRIPT_DIR_NAME/services/build-docker-image.sh" \
    $VERBOSE_FLAG \
    $TAG_FLAG \
    "$SERVICES_TAR_GZ" \
    "$USERNAME" \
    "$PASSWORD"

exit 0
