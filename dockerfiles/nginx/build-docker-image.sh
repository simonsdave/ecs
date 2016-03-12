#!/usr/bin/env bash
#
# This script builds ECS' ecs-nginx docker image
#

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

if [ "-v" == "${1:-}" ]; then
    VERBOSE=1
    shift
else
    VERBOSE=0
fi

if [ $# != 1 ] && [ $# != 3 ]; then
    echo "usage: `basename $0` [-v] <username> [<email> <password>]" >&2
    exit 1
fi

USERNAME=${1:-}
EMAIL=${2:-}
PASSWORD=${3:-}

IMAGENAME=$USERNAME/ecs-nginx
sudo docker build -t $IMAGENAME "$SCRIPT_DIR_NAME"
if [ "$EMAIL" != "" ]; then
    sudo docker login --email="$EMAIL" --username="$USERNAME" --password="$PASSWORD"
    sudo docker push $IMAGENAME
fi

exit 0
