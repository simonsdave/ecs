#!/usr/bin/env bash
#
# This script builds ECS' ecs-apidocs docker image
#

set -e

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

VERBOSE=0
TAG="latest"

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
            TAG=$1
            shift
            ;;
        *)
            break
            ;;
    esac
done

if [ $# != 2 ] && [ $# != 3 ]; then
    echo "usage: `basename $0` [-v] [-t <tag>] <api-docs-tar> <username> [<password>]" >&2
    exit 1
fi

API_DOCS_TAR=${1:-}
USERNAME=${2:-}
PASSWORD=${3:-}

IMAGENAME=$USERNAME/ecs-apidocs:$TAG

cp "$API_DOCS_TAR" "$SCRIPT_DIR_NAME/api_docs.tar"
docker build -t $IMAGENAME "$SCRIPT_DIR_NAME"
rm "$SCRIPT_DIR_NAME/api_docs.tar"

if [ "$PASSWORD" != "" ]; then
    docker login --username="$USERNAME" --password="$PASSWORD"
    docker push $IMAGENAME
fi

exit 0
