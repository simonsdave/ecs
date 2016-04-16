#!/usr/bin/env bash

if [ "-v" == "${1:-}" ]; then
    VERBOSE=1
    shift
else
    VERBOSE=0
fi

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

if [ $# != 0 ] && [ $# != 1 ]; then
    echo "usage: `basename $0` [-v] [ecs endpoint]" >&2
    exit 1
fi

if [ $# == 0 ]; then
    ECS_ADDRESS=127.0.0.1
    ECS_PORT=9448

    ECS_ENDPOINT="http://$ECS_ADDRESS:$ECS_PORT"

    ECS_CONFIG_FILE=$(mktemp 2> /dev/null || mktemp -t DAS)
    echo "[ecs]" >> "$ECS_CONFIG_FILE"
    echo "address=$ECS_ADDRESS" >> "$ECS_CONFIG_FILE"
    echo "port=$ECS_PORT" >> "$ECS_CONFIG_FILE"
    echo "log_level=info" >> "$ECS_CONFIG_FILE"
    echo "max_concurrent_executing_http_requests=250" >> "$ECS_CONFIG_FILE"
    echo "docker_remote_api=http://172.17.42.1:2375" >> "$ECS_CONFIG_FILE"
    echo "docker_remote_api_connect_timeout=3000" >> "$ECS_CONFIG_FILE"
    echo "docker_remote_api_request_timeout=300000" >> "$ECS_CONFIG_FILE"

    ECS_LOG_FILE=$(mktemp 2> /dev/null || mktemp -t DAS)
    ecservice.py --config="$ECS_CONFIG_FILE" >& /dev/null &
    ECS_PID=$!

    if [ $VERBOSE == 1 ]; then
        echo "Started ECS - PID = $ECS_PID; config file  '$ECS_CONFIG_FILE'"
    fi
else
    ECS_ENDPOINT=$1
fi

LOCUST_LOG_FILE=$(mktemp 2> /dev/null || mktemp -t DAS)
LOCUST_OUTPUT_FILE=$(mktemp 2> /dev/null || mktemp -t DAS)

if [ $VERBOSE == 1 ]; then
    echo "Find locust log file @ '$LOCUST_LOG_FILE'"
    echo "Find locust output @ '$LOCUST_OUTPUT_FILE'"
fi

locust \
    --locustfile="$SCRIPT_DIR_NAME/locustfile.py" \
    --no-web \
    --num-request=1000 \
    --clients=25 \
    --hatch-rate=5 \
    --host=$ECS_ENDPOINT \
    --logfile="$LOCUST_LOG_FILE" \
    >& "$LOCUST_OUTPUT_FILE"

"$SCRIPT_DIR_NAME/analyze_load_test_tsv.py" < "$LOCUST_LOG_FILE"

if [ "${ECS_PID:-}" != "" ]; then
    kill $ECS_PID
fi

exit 0
