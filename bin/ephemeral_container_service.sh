#!/usr/bin/env bash
#
# this script is a wrapper around ephemeral_container_service.py
#

if [ "-v" == "${1:-}" ]; then
    VERBOSE=1
    shift
else
    VERBOSE=0
fi

if [ $# != 1 ]; then
    echo "usage: `basename $0` [-v] <config-tar-file-url>" >&2
    exit 1
fi

CONFIG_TAR_FILE_URL=${1:-}

CONFIG_DIR=~/.ecs
rm -rf "$CONFIG_DIR"
mkdir -p "$CONFIG_DIR"

TEMP_CONFIG_DIR=$(mktemp -d 2> /dev/null || mktemp -d -t DAS)
pushd "$TEMP_CONFIG_DIR" > /dev/null

DOWNLOADED_CONFIG_TAR_FILENAME=config.tar

curl -s -o "$DOWNLOADED_CONFIG_TAR_FILENAME" "$CONFIG_TAR_FILE_URL"
if [ $? -ne 0 ] ; then
    echo "error downloading config tar file from '$CONFIG_TAR_FILE_URL'" >&2
    exit 2
fi

tar xvf "$DOWNLOADED_CONFIG_TAR_FILENAME"
if [ $? -ne 0 ] ; then
    echo "error exploding tar file downloaded from '$CONFIG_TAR_FILE_URL'" >&2
    exit 3
fi
rm "$DOWNLOADED_CONFIG_TAR_FILENAME"

cp -R * "$CONFIG_DIR"
if [ $? -ne 0 ] ; then
    echo "error copying downloaded config '$CONIG_DIR'" >&2
    exit 4
fi

popd > /dev/null

rm -r "$TEMP_CONFIG_DIR"

ephemeral_container_service.py --config=$CONFIG_DIR/config

exit 0
