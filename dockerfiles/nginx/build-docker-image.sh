#!/usr/bin/env bash
#
# This script builds ECS' ecs-nginx docker image
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

if [ $# != 1 ] && [ $# != 2 ]; then
    echo "usage: `basename $0` [-v] [-t <tag>] <username> [<password>]" >&2
    exit 1
fi

USERNAME=${1:-}
PASSWORD=${2:-}

IMAGENAME=$USERNAME/ecs-nginx:$TAG

docker build -t $IMAGENAME "$SCRIPT_DIR_NAME"

if [ "$PASSWORD" != "" ]; then
    docker login --username="$USERNAME" --password="$PASSWORD"
    docker push $IMAGENAME
fi

exit 0
