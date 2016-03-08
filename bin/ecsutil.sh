#
# all the scripts which source util.sh take an optional
# -v command line option. the few statements below set
# the VERBOSE env var based on the presence/absence of
# this option.
#
if [ "-v" == "${1:-}" ]; then
    VERBOSE=1
    shift
else
    VERBOSE=0
fi

#
# given a value of length V, add N - V zeros to left pad the
# value so the resulting value is N digits long
#
# for example, the following script writes 000023 to stdout
#
#   #!/usr/bin/env bash
#   SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#   source $SCRIPT_DIR_NAME/util.sh
#   left_zero_pad 23 6
#
left_zero_pad() {
    VALUE=${1:-}
    DESIRED_NUMBER_DIGITS=${2:-}
    python -c "print ('0'*10+'$VALUE')[-$DESIRED_NUMBER_DIGITS:]"
}

#
# write the first argument to this function (which is assumed
# to be a string) to stdout formatting the string as per the
# second argument. the second optional argument is a string with
# a list of formatting words seperated by a space. valid formatting
# words are bold, yellow, red, blue.
#
# arguments
#   1   string to format
#   2   format string
#
# exit codes
#   0   always
#
echo_formatted() {

    for FORMAT in $(echo ${2:-} | tr " " "\n")
    do
        FORMAT=$(echo $FORMAT | awk "{print toupper(\"$FORMAT\")}")
        case "$FORMAT" in
            BOLD)
                echo -n "$(tput bold)"
                ;;
            RED)
                echo -n "$(tput setaf 1)"
                ;;
            YELLOW)
                echo -n "$(tput setaf 3)"
                ;;
            BLUE)
                echo -n "$(tput setaf 4)"
                ;;
            *)
                ;;
        esac
    done

    echo "${1:-}$(tput sgr0)"

    return 0
}

#
# write the first argument to this function (which is assumed
# to be a string) to stderr
#
# arguments
#   1   string to write to stderr
#   2   format string (see echo_formatted)
#
# exit codes
#   0   always
#
echo_to_stderr() {
    echo $(echo_formatted "${1:-}" "${2:-}") >&2
    return 0
}

#
# if the variable $VERBOSE is 1 then the first argument to this
# function is assumed to be a string and the function echo's
# the string to stdout
#
# arguments
#   1   string to write to stdout
#   2   format string (see echo_formatted)
#
# exit codes
#   0   always
#
echo_if_verbose() {
    if [ 1 -eq ${VERBOSE:-0} ]; then
        echo $(echo_formatted "${1:-}" "${2:-}")
    fi
    return 0
}

#
# if the variable $VERBOSE is 1 then the first argument to this
# function is assumed to be a file name and the function cats the
# contents of the file to stdout
#
# arguments
#   1   name of file to cat to stdout
#
# exit codes
#   0   always
#
cat_if_verbose() {
    if [ 1 -eq ${VERBOSE:-0} ]; then
        cat $1
    fi
    return 0
}

#
# a few BASH script should be able to run on both Ubuntu
# and OS X - mktemp operates slightly differently on these
# two platforms - this function insulates scripts from
# the differences
#
# exit codes
#   0   always
#
platform_safe_mktemp() {
    mktemp 2> /dev/null || mktemp -t DAS
    return 0
}

#
# a few BASH script should be able to run on both Ubuntu
# and OS X - mktemp operates slightly differently on these
# two platforms - this function insulates scripts from
# the differences
#
# exit codes
#   0   always
#
platform_safe_mktemp_directory() {
    mktemp -d 2> /dev/null || mktemp -d -t DAS
    return 0
}

#
# creates a keyczar key store
#
# arguments
#   1   name of directory in which to create the key store
#
# exit codes
#   0   always
#
create_keyczar_key_store() {
    mkdir -p "$1"
    keyczart create --location="$1" --purpose=crypt
    keyczart addkey --location="$1" --status=primary
    return 0
}

#
# creates a self-signed key pair
#
# arguments
#   1   private key filename (probably ends in .key)
#   2   cert filename (probably ends in .pem)
#
# exit codes
#   0   always
#
create_self_signed_cert() {
    local KEY_FILE=$1
    local CERT_FILE=$2

    local CSR_FILE=$(platform_safe_mktemp)
    local TEMP_KEY_FILE=$(platform_safe_mktemp)

    local PASSWORD=password

    openssl genrsa -des3 -passout pass:$PASSWORD -out "$KEY_FILE" 2048 >& /dev/null
    openssl req -new -batch -key "$KEY_FILE" -passin pass:$PASSWORD -out "$CSR_FILE" >& /dev/null
    cp "$KEY_FILE" "$TEMP_KEY_FILE"
    openssl rsa -in "$TEMP_KEY_FILE" -passin pass:$PASSWORD -out "$KEY_FILE" >& /dev/null
    rm "$TEMP_KEY_FILE"
    openssl x509 -req -days 365 -in "$CSR_FILE" -signkey "$KEY_FILE" -out "$CERT_FILE" >& /dev/null
    rm "$CSR_FILE"

    return 0
}

#
# Search the Google Compute Cloud's SDK configuration for the
# current project's zone and echo it to stdout. If no zone
# is found nothing is echoed to stdout.
#
# exit codes
#   0   always
#
get_zone() {
    gcloud config list | grep "^zone = " | sed -e "s/zone = //g"
    return 0
}

#
# Search the Google Compute Cloud's SDK configuration for the
# current project's zone, infer the region from the zone and
# echo the region to stdout. If no region is found nothing is
# echoed to stdout.
#
# exit codes
#   0   always
#
get_region() {
    get_zone | sed -e "s/-[a-z]$//g"
}

#
# this function create a pip installable zip file
# of the Identity Service
#
# exit codes
#   0   always
#
create_dist() {
    local SOURCE_DIR=${1:-}
    pushd "$SOURCE_DIR" > /dev/null
    local TEMP_OUTPUT_FILE=$(platform_safe_mktemp)
    if ! python setup.py sdist --formats=gztar >& "$TEMP_OUTPUT_FILE"; then
        cat "$TEMP_OUTPUT_FILE"
        exit 1
    fi
    popd > /dev/null
    return 0
}
