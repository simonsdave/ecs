#!/usr/bin/env bash

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

rm "$SCRIPT_DIR_NAME/raw_data.tsv" >& /dev/null

locust \
    --locustfile="$SCRIPT_DIR_NAME/locustfile.py" \
    --no-web \
    --num-request=1000 \
    --clients=25 \
    --hatch-rate=5 \
    --host=http://127.0.0.1:8448 \
    --logfile="$SCRIPT_DIR_NAME/raw_data.tsv"

exit 0
