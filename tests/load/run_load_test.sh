#!/usr/bin/env bash

#
# exit codes
#
#   0   ok
#   1   usage error
#   2   config file not readable
#

if [ "-v" == "${1:-}" ]; then
    VERBOSE=1
    shift
else
    VERBOSE=0
fi

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

if [ $# != 1 ]; then
    echo "usage: `basename $0` [-v] <load test config>" >&2
    exit 1
fi

LOAD_TEST_CONFIG=${1:-}
if [ ! -r "$LOAD_TEST_CONFIG" ]; then
    echo "Can't read from config file '$LOAD_TEST_CONFIG'" >&2
    exit 2
fi

ECS_ENDPOINT=$(cat "$LOAD_TEST_CONFIG" | jq -r .endpoint | sed -e 's/null//g')
if [ "$ECS_ENDPOINT" == "" ]; then
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
        echo "$(tput bold)Started ECS - PID = $ECS_PID; config file '$ECS_CONFIG_FILE'$(tput sgr0)"
    fi
fi

for i in $(seq 0 50)
do
    ECS_CONCURRENCY=$(cat "$LOAD_TEST_CONFIG" | jq -r .concurrency[$i] | sed -e 's/null//g')
    if [ "$ECS_CONCURRENCY" == "" ]; then
        break
    fi

    ECS_NUMBER_OF_REQUESTS=$(cat "$LOAD_TEST_CONFIG" | jq -r .number_of_requests | sed -e "s/null/1000/g")

    ECS_HATCH_RATE=$(cat "$LOAD_TEST_CONFIG" | jq -r .hatch_rate | sed -e "s/null/5/g")
    
    LOCUST_LOG_FILE=$(mktemp 2> /dev/null || mktemp -t DAS)
    LOCUST_OUTPUT_FILE=$(mktemp 2> /dev/null || mktemp -t DAS)

    if [ $VERBOSE == 1 ]; then
        echo "$(tput bold)Find locust log file @ '$LOCUST_LOG_FILE' for $ECS_CONCURRENCY concurrency$(tput sgr0)"
        echo "$(tput bold)Find locust output @ '$LOCUST_OUTPUT_FILE' for $ECS_CONCURRENCY concurrency$(tput sgr0)"
    fi

    ECS_CREDENTIALS=$(cat "$LOAD_TEST_CONFIG" | jq -r .credentials | sed -e 's/null//g')

    ECS_CREDENTIALS=$ECS_CREDENTIALS locust \
        --locustfile="$SCRIPT_DIR_NAME/locustfile.py" \
        --no-web \
        --num-request=$ECS_NUMBER_OF_REQUESTS \
        --clients=$ECS_CONCURRENCY \
        --hatch-rate=$ECS_HATCH_RATE \
        --host=$ECS_ENDPOINT \
        --logfile="$LOCUST_LOG_FILE" \
        >> "$LOCUST_OUTPUT_FILE" 2>&1

    "$SCRIPT_DIR_NAME/analyze_load_test_tsv.py" < "$LOCUST_LOG_FILE"
done

if [ "${ECS_PID:-}" != "" ]; then
    kill $ECS_PID
fi

exit 0
