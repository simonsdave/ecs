#!/usr/bin/env bash
#
# This script builds ECS' ecs-nginx docker image
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

if [ $# != 1 ] && [ $# != 3 ]; then
    echo "usage: `basename $0` [-v] [-t <tag>] <username> [<email> <password>]" >&2
    exit 1
fi

USERNAME=${1:-}
EMAIL=${2:-}
PASSWORD=${3:-}

IMAGENAME=$USERNAME/ecs-nginx
if [ "$TAG" != "" ]; then
    IMAGENAME=$IMAGENAME:$TAG
fi

docker build -t $IMAGENAME "$SCRIPT_DIR_NAME"

if [ "$EMAIL" != "" ]; then
    docker login --email="$EMAIL" --username="$USERNAME" --password="$PASSWORD"
    docker push $IMAGENAME
fi

exit 0
