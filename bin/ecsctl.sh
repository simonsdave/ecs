#!/usr/bin/env bash
#
# this script spins up an ECS deployment
# in the Google Compute Cloud
#

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
source "$SCRIPT_DIR_NAME/ecsutil.sh"

NETWORK_NAME=ecs

# note - see note associated with NUMBER_NODES on how choosing
# this machine type needs to be done with consideration of the entire
# deployment
MACHINE_TYPE=n1-standard-2

# name of the image for each node in the cluster
# see https://coreos.com/os/docs/latest/booting-on-google-compute-engine.html#choosing-a-channel
IMAGE_NAME=https://www.googleapis.com/compute/v1/projects/coreos-cloud/global/images/coreos-stable-899-13-0-v20160323

# regions and zones within regions
# all resources are either zonal or regional

# load balances (or fowarding rules in GCE land) load
# balance across collections of VM instances where the
# VM instances are in the same target pool
TARGET_POOL_NAME=$NETWORK_NAME-target-pool

# target pools issue periodic http health checks to confirm
# instances are healthy. HTTP_HEALTH_CHECK_NAME is the name
# of the ECS health check
HTTP_HEALTH_CHECK_NAME=health-check
HTTP_HEALTH_CHECK_PORT=8080
HTTP_HEALTH_CHECK_PATH=/_only_for_lb_health_check

# creating a forwarding rule is like creating a load balancer
FORWARDING_RULE_NAME=$NETWORK_NAME-forwarding-rule

create_http_health_check() {
    local HTTP_HEALTH_CHECK_NAME=${1:-}
    local HTTP_HEALTH_CHECK_PORT=${2:-}
    local HTTP_HEALTH_CHECK_PATH=${3:-}
    local TARGET_POOL_NAME=${4:-}

    echo_if_verbose "Creating http health check '$HTTP_HEALTH_CHECK_NAME'"

    gcloud \
        compute http-health-checks create $HTTP_HEALTH_CHECK_NAME \
        --request-path $HTTP_HEALTH_CHECK_PATH \
        --port $HTTP_HEALTH_CHECK_PORT \
        --quiet \
        >& /dev/null

    gcloud \
        compute target-pools add-health-checks $TARGET_POOL_NAME \
        --http-health-check $HTTP_HEALTH_CHECK_NAME \
        --region $(get_region) \
        --quiet \
        >& /dev/null

    echo_if_verbose "Created http health check '$HTTP_HEALTH_CHECK_NAME'"

    return 0
}

delete_http_health_check() {
    local HTTP_HEALTH_CHECK_NAME=${1:-}
    local TARGET_POOL_NAME=${2:-}

    echo_if_verbose "Deleting http health check '$HTTP_HEALTH_CHECK_NAME'"

    gcloud \
        compute target-pools remove-health-checks $TARGET_POOL_NAME \
        --http-health-check $HTTP_HEALTH_CHECK_NAME \
        --region $(get_region) \
        --quiet \
        >& /dev/null

    gcloud \
        compute http-health-checks delete $HTTP_HEALTH_CHECK_NAME \
        --quiet \
        >& /dev/null

    echo_if_verbose "Deleted http health check '$HTTP_HEALTH_CHECK_NAME'"

    return 0
}

create_firewall_rules() {
    gcloud \
        compute firewall-rules create $NETWORK_NAME-allow-icmp \
        --quiet \
        --network $NETWORK_NAME \
        --allow icmp

    gcloud \
        compute firewall-rules create $NETWORK_NAME-allow-ssh \
        --quiet \
        --network $NETWORK_NAME \
        --allow tcp:22

    gcloud \
        compute firewall-rules create $NETWORK_NAME-allow-internal \
        --quiet \
        --network $NETWORK_NAME \
        --source-ranges '10.240.0.0/16' \
        --allow tcp:1-65535,udp:1-65535,icmp

    gcloud \
        compute firewall-rules create $NETWORK_NAME-allow-http \
        --quiet \
        --network $NETWORK_NAME \
        --allow tcp:80

    gcloud \
        compute firewall-rules create $NETWORK_NAME-allow-https \
        --quiet \
        --network $NETWORK_NAME \
        --allow tcp:443

    return 0
}

delete_firewall_rules() {
    for FIREWALL_RULE_NAME in $(gcloud compute firewall-rules list --regexp ^$NETWORK_NAME.*$ | tail -n +2 | awk '{print $1}'); do
        gcloud compute firewall-rules delete --quiet $FIREWALL_RULE_NAME
    done

    return 0
}

create_target_pool() {
    echo_if_verbose "Creating target pool '$TARGET_POOL_NAME'"

    gcloud \
        compute target-pools create \
        --quiet \
        $TARGET_POOL_NAME \
        --region $(get_region) \
        >& /dev/null
    if [ $? -ne 0 ] ; then
        echo_to_stderr "Error creating target pool '$TARGET_POOL_NAME'"
        exit 1
    fi

    echo_if_verbose "Successfully created target pool '$TARGET_POOL_NAME'"
    return 0
}

delete_target_pool() {
    gcloud \
        compute target-pools delete \
        --quiet \
        $TARGET_POOL_NAME \
        --region $(get_region) \
        >& /dev/null
    echo_if_verbose "Deleted target pool '$TARGET_POOL_NAME'"
    return 0
}

create_forwarding_rule() {
    gcloud \
        compute forwarding-rules create \
        --quiet \
        $FORWARDING_RULE_NAME \
        --target-pool $TARGET_POOL_NAME \
        --region $(get_region) \
        --ip-protoco TCP \
        --port-range 80-443 \
        >& /dev/null
    if [ $? -ne 0 ] ; then
        exit 1
    fi

    gcloud \
        compute forwarding-rules describe $FORWARDING_RULE_NAME \
        --region $(get_region) | \
        grep IPAddress | \
        sed -e "s/IPAddress: //g"
}

delete_forwarding_rule() {
    gcloud \
        compute forwarding-rules delete \
        --quiet \
        $FORWARDING_RULE_NAME \
        --region $(get_region) \
        >& /dev/null
    echo_if_verbose "Deleted forwarding rule '$FORWARDING_RULE_NAME'"
    return 0
}

deployment_create_network() {
    echo_if_verbose "Creating Network" "blue"
    gcloud compute networks create $NETWORK_NAME

    echo_if_verbose "Creating Firewall Rules" "blue"
    create_firewall_rules

    echo_if_verbose "Creating Target Pool" "blue"
    create_target_pool

    echo_if_verbose "Creating Forwarding Rule" "blue"
    local FORWARDING_RULE_IP=$(create_forwarding_rule)
    echo "Access ECS cluster @ $FORWARDING_RULE_IP"

    create_http_health_check \
        $HTTP_HEALTH_CHECK_NAME \
        $HTTP_HEALTH_CHECK_PORT \
        $HTTP_HEALTH_CHECK_PATH \
        $TARGET_POOL_NAME
}

deployment_inspect_network() {
    echo_if_verbose "Firewall Rule(s)" "blue"
    gcloud compute firewall-rules list --regexp ^$NETWORK_NAME.*$

    echo_if_verbose "Target Pool(s)" "blue"
    gcloud compute target-pools list --regexp ^$NETWORK_NAME.*$

    echo_if_verbose "Forwarding Rule(s)" "blue"
    gcloud compute forwarding-rules list --region $(get_region) --regexp ^$NETWORK_NAME.*$
}

deployment_delete_network() {
    delete_http_health_check $HTTP_HEALTH_CHECK_NAME $TARGET_POOL_NAME

    echo_if_verbose "Deleting Forwarding Rule(s)" "blue"
    delete_forwarding_rule

    echo_if_verbose "Deleting Target Pool(s)" "blue"
    delete_target_pool

    echo_if_verbose "Deleting Firewall Rule(s)" "blue"
    delete_firewall_rules

    echo_if_verbose "Deleting Network(s)" "blue"
    gcloud compute networks delete --quiet $NETWORK_NAME
}

get_instance_ip() {
    local INSTANCE_NAME=${1:-}
    gcloud \
        compute instances describe $INSTANCE_NAME | \
        grep natIP | \
        sed -e "s/natIP://g"
}

deployment_create_cloud_config() {
    local DOCS_DOMAIN=${1:-}
    local API_DOMAIN=${2:-}
    local DOCS_CERT=${3:-}
    local DOCS_KEY=${4:-}
    local API_CERT=${5:-}
    local API_KEY=${6:-}
    local API_CREDENTIALS=${7:-}
    local DHPARAM_PEM=${8:-}
    local NUMBER_OF_NODES=${9:-}

    local CLOUD_CONFIG=$(platform_safe_mktemp)
    local CLOUD_CONFIG_TEMPLATE=$SCRIPT_DIR_NAME/ecs-cloud-config-template.yaml

    local DISCOVERY_TOKEN=$(curl -s "https://discovery.etcd.io/new?size=$NUMBER_OF_NODES")

    # this sed mess is required because URLs may contain the & character
    # which is interpreted in a special manner by the "s" command:-(
    local SED_SCRIPT_1=$(platform_safe_mktemp)
    echo "s|%DISCOVERY_TOKEN%|$DISCOVERY_TOKEN|g" >> "$SED_SCRIPT_1"
    echo "s|%DOCS_DOMAIN%|$DOCS_DOMAIN|g" >> "$SED_SCRIPT_1"
    echo "s|%API_DOMAIN%|$API_DOMAIN|g" >> "$SED_SCRIPT_1"
    local SED_SCRIPT_2=$(platform_safe_mktemp)
    cat "$SED_SCRIPT_1" | sed -e 's/&/\\\&/g' > "$SED_SCRIPT_2"
    cat "$CLOUD_CONFIG_TEMPLATE" | sed -f "$SED_SCRIPT_2" > "$CLOUD_CONFIG"

    deployment_indent_and_insert_file_into_cloud_config "$CLOUD_CONFIG" %API_CERT% "$API_CERT"
    deployment_indent_and_insert_file_into_cloud_config "$CLOUD_CONFIG" %API_KEY% "$API_KEY"

    deployment_indent_and_insert_file_into_cloud_config "$CLOUD_CONFIG" %DOCS_CERT% "$DOCS_CERT"
    deployment_indent_and_insert_file_into_cloud_config "$CLOUD_CONFIG" %DOCS_KEY% "$DOCS_KEY"

    deployment_indent_and_insert_file_into_cloud_config "$CLOUD_CONFIG" %API_CREDENTIALS% "$API_CREDENTIALS"
    deployment_indent_and_insert_file_into_cloud_config "$CLOUD_CONFIG" %DHPARAM_PEM% "$DHPARAM_PEM"

    echo $CLOUD_CONFIG
}

deployment_indent_and_insert_file_into_cloud_config() { 
    local CLOUD_CONFIG=${1:-}
    local VARIABLE=${2:-}
    local CERT_OR_KEY=${3:-}

    local TEMP_CERT_CONFIG_DIR=$(platform_safe_mktemp_directory)
    pushd $TEMP_CERT_CONFIG_DIR > /dev/null

    local INDENT=$(grep ^\\s*$VARIABLE\\s*$ "$CLOUD_CONFIG" | sed -e "s|$VARIABLE\s*$||g")
    local INDENTED_CERT=$(platform_safe_mktemp)
    sed "s/^/$INDENT/" < "$CERT_OR_KEY" > "$INDENTED_CERT"
    csplit --quiet - /^\\s*$VARIABLE\\s*$/ < "$CLOUD_CONFIG"
    tail -n +2 xx01 > xx02
    cat xx00 "$INDENTED_CERT" xx02 > "$CLOUD_CONFIG"

    popd > /dev/null

    rm -rf "$TEMP_CERT_CONFIG_DIR"
}

deployment_create_node() {
    echo_if_verbose "Starting new node" "blue"

    local CLOUD_CONFIG=${1:-}

    INSTANCE_NAME="$NETWORK_NAME-$(python -c 'import uuid; print uuid.uuid4().hex')"

    gcloud \
        compute instances create $INSTANCE_NAME \
        --machine-type $MACHINE_TYPE \
        --image $IMAGE_NAME \
        --network $NETWORK_NAME \
        --tags $NETWORK_NAME-node \
        --metadata-from-file user-data=$CLOUD_CONFIG \
        >& /dev/null
    if [ $? -ne 0 ] ; then
        echo_to_stderr "Error creating node '$INSTANCE_NAME'"
        exit 1
    fi

    gcloud \
        compute target-pools --quiet add-instances $TARGET_POOL_NAME \
        --instances $INSTANCE_NAME \
        >& /dev/null
    if [ $? -ne 0 ] ; then
        echo_to_stderr "Error adding node '$INSTANCE_NAME' to target pool '$TARGET_POOL_NAME'"
        exit 1
    fi

    echo_if_verbose "Successfully started node '$INSTANCE_NAME'"

    return 0
}

deployment_delete_node() {
    local INSTANCE_NAME=${1:-}

    echo_if_verbose "Deleting node '$INSTANCE_NAME'" "blue"
    gcloud \
        compute target-pools \
        --quiet \
        remove-instances $TARGET_POOL_NAME \
        --instances $INSTANCE_NAME \
        >& /dev/null

    gcloud \
        compute instances --quiet delete $INSTANCE_NAME \
        >& /dev/null

    echo_if_verbose "Deleted node '$INSTANCE_NAME'"
}

deployment_create() {
    echo_if_verbose "Creating Deployment" "yellow"

    deployment_create_network

    local CLOUD_CONFIG=$(deployment_create_cloud_config "$@")
    local NUMBER_OF_NODES=${9:-}

    for i in `seq 1 $NUMBER_OF_NODES`; do
        deployment_create_node "$CLOUD_CONFIG"
    done

    exit 0

}

deployment_inspect() {
    echo_if_verbose "Inspecting Deployment" "yellow"
    deployment_inspect_network

    echo_if_verbose "Instances" "yellow"
    gcloud compute instances list --regexp ^$NETWORK_NAME.*$
}

deployment_delete() {
    echo_if_verbose "Deleting Deployment" "yellow"

    for INSTANCE_NAME in $(gcloud compute instances list --regexp ^$NETWORK_NAME.*$ | tail -n +2 | awk '{print $1}'); do
        deployment_delete_node $INSTANCE_NAME
    done

    deployment_delete_network
}

deployment_usage() {
    echo "usage: `basename $0` [-v] dep <command> ..."
    echo ""
    echo "The most commonly used dep commands are:"
    echo "  create       spin up an ECS deployment"
    echo "  inspect      inspect the details of a previously created deployment"
    echo "  remove       remove a previously created deployment"
}

deployment_cmd() {
    local COMMAND=`echo ${1:-} | awk '{print toupper($0)}'`
    shift
    case "$COMMAND" in
        CR|CREATE)
            if [ $# != 9 ]; then
                echo "usage: `basename $0` [-v] deploy create <docs_domain> <api_domain> <docs_cert> <docs_key> <api_cert> <api_key> <api_credentials> <dhparam> <number_of_nodes>"
                exit 1
            fi

            deployment_create "$@"
            ;;

        INS|INSPECT)
            if [ $# != 0 ]; then
                echo "usage: `basename $0` [-v] deploy inspect"
                exit 1
            fi

            deployment_inspect
            ;;

        RM|REMOVE|DEL|DELETE)
            if [ $# != 0 ]; then
                echo "usage: `basename $0` [-v] deploy remove"
                exit 1
            fi

            deployment_delete
            ;;

        *)
            deployment_usage
            exit 1
            ;;
    esac
}

creds_cmd() {
    if [ $# != 0 ] && [ $# != 1 ]; then
        echo "usage: `basename $0` [-v] creds [number_of_creds]" >&2
        exit 1
    fi

    local NUMBER_OF_CREDS=${1:-5}

    local DOT_HTPASSWD=$PWD/.htpasswd

    if [ -e "$DOT_HTPASSWD" ]; then
        echo "Adding hashed credentials to existing file '$DOT_HTPASSWD'"
    else
        echo "Putting hashed credentials in new file '$DOT_HTPASSWD'"
        touch "$DOT_HTPASSWD"
    fi

    for i in `seq 1 $NUMBER_OF_CREDS`;
    do
        local KEY=$(python -c "import uuid; print uuid.uuid4().hex")
        local SECRET=$(python -c "import binascii; import os; print binascii.b2a_hex(os.urandom(128/8))")
        #
        # -b = batch
        #
        # wanted to use bcrypt to hash secrets so the htpasswd command would be 
        #
        #   htpasswd -b -B -C 12 "$DOT_HTPASSWD" $KEY $SECRET > /dev/null 2>&1
        #
        # where
        #
        #   -B = bcrypt for password encryption
        #   -C = # of bcrypt rounds (default 4; valid = 4 thru 31)
        #
        # but when using bcrypt nginx generated errors (in nginx error log) like
        #
        #   crypt_r() failed (22: Invalid argument)
        #
        # :TODO: don't like swallowing stderr but couldn't find another
        # way to surpress htpasswd's output
        #
        htpasswd -b "$DOT_HTPASSWD" $KEY $SECRET > /dev/null 2>&1
        echo "$KEY:$SECRET"
    done 
}

usage() {
    echo "usage: `basename $0` [-v] <command> ..."
    echo ""
    echo "The most commonly used `basename $0` commands are:"
    echo "  deploy   manage an ECS deployment"
    echo "  creds    create credentials for an ECS deployment"
}

COMMAND=`echo ${1:-} | awk '{print toupper($0)}'`
shift
case "$COMMAND" in
    DEP|DEPLOY|DEPLOYMENT)
        deployment_cmd "$@"
        ;;
    CREDS)
        creds_cmd "$@"
        ;;
    *)
        usage
        exit 1
        ;;
esac

exit 0
