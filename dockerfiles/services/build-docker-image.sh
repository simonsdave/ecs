#!/usr/bin/env bash
#
# This script builds ECS' ecs-services docker image
#

set -x

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

if [ $# != 2 ] && [ $# != 4 ]; then
    echo "usage: `basename $0` [-v] [-t <tag>] <services-tar-gz> <username> [<email> <password>]" >&2
    exit 1
fi

SERVICES_TAR_GZ=${1:-}
USERNAME=${2:-}
EMAIL=${3:-}
PASSWORD=${4:-}

IMAGENAME=$USERNAME/ecs-services
if [ "$TAG" != "" ]; then
    IMAGENAME=$IMAGENAME:$TAG
fi

cp "$SERVICES_TAR_GZ" "$SCRIPT_DIR_NAME/services.tar.gz"
docker build -t "$IMAGENAME" "$SCRIPT_DIR_NAME"
rm "$SCRIPT_DIR_NAME/services.tar.gz"

if [ "$EMAIL" != "" ]; then
    docker login --email="$EMAIL" --username="$USERNAME" --password="$PASSWORD"
    docker push $IMAGENAME
fi

exit 0
