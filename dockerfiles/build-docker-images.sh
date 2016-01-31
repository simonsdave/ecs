#!/usr/bin/env bash
#
# this script builds all of ecs's docker images
#

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

if [ "-v" == "${1:-}" ]; then
    VERBOSE=1
    shift
else
    VERBOSE=0
fi

if [ "-p" == "${1:-}" ]; then
    PUSH_TO_DOCKERHUB=1
    shift
else
    PUSH_TO_DOCKERHUB=0
fi

if [ $# != 5 ]; then
    echo "usage: `basename $0` [-v] [-p] <email> <username> <password> <services-tar-gz> <api-docs-tar>" >&2
    exit 1
fi

#
# extract and verify command line args
#
EMAIL=${1:-}
USERNAME=${2:-}
PASSWORD=${3:-}
SERVICES_TAR_GZ=${4:-}
API_DOCS_TAR=${5:-}

if [ ! -r "$SERVICES_TAR_GZ" ]; then
    echo "can't find source dist '$SERVICES_TAR_GZ'" >&2
fi

if [ ! -r "$API_DOCS_TAR" ]; then
    echo "can't find api docs tar file '$API_DOCS_TAR'" >&2
fi

#
# login to dockerhub
#
sudo docker login --email="$EMAIL" --username="$USERNAME" --password="$PASSWORD"

#
# build & optionally push nginx image
#
IMAGENAME=$USERNAME/ecs-nginx
sudo docker build -t $IMAGENAME "$SCRIPT_DIR_NAME/nginx"
if [ $PUSH_TO_DOCKERHUB == 1 ]; then
    sudo docker push $IMAGENAME
fi

#
# build & optionally push api docs image
#
cp "$API_DOCS_TAR" "$SCRIPT_DIR_NAME/apidocs/api_docs.tar"
IMAGENAME=$USERNAME/ecs-apidocs
sudo docker build -t $IMAGENAME "$SCRIPT_DIR_NAME/apidocs"
if [ $PUSH_TO_DOCKERHUB == 1 ]; then
    sudo docker push $IMAGENAME
fi

#
# build & optionally push services image
#
cp "$SERVICES_TAR_GZ" "$SCRIPT_DIR_NAME/services/services.tar.gz"
IMAGENAME=$USERNAME/ecs-services
sudo docker build -t $IMAGENAME "$SCRIPT_DIR_NAME/services"
if [ $PUSH_TO_DOCKERHUB == 1 ]; then
    sudo docker push $IMAGENAME
fi

exit 0
