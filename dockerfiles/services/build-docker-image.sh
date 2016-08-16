#!/usr/bin/env bash
#
# This script builds ECS' ecs-services docker image
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
    echo "usage: `basename $0` [-v] [-t <tag>] <services-tar-gz> <username> [<password>]" >&2
    exit 1
fi

SERVICES_TAR_GZ=${1:-}
USERNAME=${2:-}
PASSWORD=${3:-}

IMAGENAME=$USERNAME/ecs-services:$TAG

cp "$SERVICES_TAR_GZ" "$SCRIPT_DIR_NAME/services.tar.gz"
docker build -t "$IMAGENAME" "$SCRIPT_DIR_NAME"
rm "$SCRIPT_DIR_NAME/services.tar.gz"

if [ "$PASSWORD" != "" ]; then
    docker login --username="$USERNAME" --password="$PASSWORD"
    docker push $IMAGENAME
fi

exit 0
