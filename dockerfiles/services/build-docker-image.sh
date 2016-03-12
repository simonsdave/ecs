#!/usr/bin/env bash
#
# This script builds ECS' ecs-services docker image
#

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

if [ "-v" == "${1:-}" ]; then
    VERBOSE=1
    shift
else
    VERBOSE=0
fi

if [ $# != 2 ] && [ $# != 4 ]; then
    echo "usage: `basename $0` [-v] <services-tar-gz> <username> [<email> <password>]" >&2
    exit 1
fi

SERVICES_TAR_GZ=${1:-}
USERNAME=${2:-}
EMAIL=${3:-}
PASSWORD=${4:-}

cp "$SERVICES_TAR_GZ" "$SCRIPT_DIR_NAME/services.tar.gz"
IMAGENAME=$USERNAME/ecs-services
sudo docker build -t "$IMAGENAME" "$SCRIPT_DIR_NAME"
if [ "$EMAIL" != "" ]; then
    sudo docker login --email="$EMAIL" --username="$USERNAME" --password="$PASSWORD"
    sudo docker push $IMAGENAME
fi
rm "$SCRIPT_DIR_NAME/services.tar.gz"

exit 0
