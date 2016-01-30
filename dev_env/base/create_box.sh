#!/usr/bin/env bash

if [ $# != 0 ]; then
    echo "usage: `basename $0`"
    exit 1
fi

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
cd "$SCRIPT_DIR_NAME"

BOX_NAME=ecs-dev-env

vagrant destroy --force

vagrant box remove $BOX_NAME

vagrant up

vagrant package --output $BOX_NAME.box

vagrant box add $BOX_NAME $BOX_NAME.box

rm $BOX_NAME.box

vagrant destroy -f

exit 0
