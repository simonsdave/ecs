#!/usr/bin/env bash
#
# This script builds ECS' ecs-apidocs docker image
#

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

if [ "-v" == "${1:-}" ]; then
    VERBOSE=1
    shift
else
    VERBOSE=0
fi

if [ $# != 2 ] && [ $# != 4 ]; then
    echo "usage: `basename $0` [-v] <api-docs-tar> <username> [<email> <password>]" >&2
    exit 1
fi

API_DOCS_TAR=${1:-}
USERNAME=${2:-}
EMAIL=${3:-}
PASSWORD=${4:-}

cp "$API_DOCS_TAR" "$SCRIPT_DIR_NAME/api_docs.tar"
IMAGENAME=$USERNAME/ecs-apidocs
sudo docker build -t $IMAGENAME "$SCRIPT_DIR_NAME"
if [ "$EMAIL" != "" ]; then
    sudo docker login --email="$EMAIL" --username="$USERNAME" --password="$PASSWORD"
    sudo docker push $IMAGENAME
fi
rm "$SCRIPT_DIR_NAME/api_docs.tar"

exit 0
