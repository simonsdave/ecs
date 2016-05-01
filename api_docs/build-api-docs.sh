#!/usr/bin/env bash
#
# This script generates HTML API docs from a set of
# RAML files using raml2html.
#
# raml2html must be installed for this script to work. if raml2html is
# not installed this script will error out.
#
# exit codes
#   0           ok
#   non-zero    something bad

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

VERBOSE=0
CREATE_TAR_FILE=0
DEPLOY_API_DOCS=0

while true
do
    OPTION=`echo ${1:-} | awk '{print tolower($0)}'`
    case "$OPTION" in
        -d)
            shift
            DEPLOY_API_DOCS=1
            ;;
        -t)
            shift
            CREATE_TAR_FILE=1
            ;;
        -v)
            shift
            VERBOSE=1
            ;;
        *)
            break
            ;;
    esac
done

DEPLOYMENT_DIR=/usr/share/nginx/ecs/html

if [ $# != 0 ]; then
    echo "usage: `basename $0` [-v] [-d] [-t]" >&2
    exit 1
fi

which raml2html >& /dev/null
if [ $? != 0 ]; then
    echo "raml2html not installed" >&2
    exit 1
fi

html_to_raml() {
    local BASE_FILENAME=${1:-}

    local RAML="$SCRIPT_DIR_NAME/$BASE_FILENAME.raml"
    local HTML="$SCRIPT_DIR_NAME/$BASE_FILENAME.html"
    local DEPLOYMENT_HTML="$DEPLOYMENT_DIR/$BASE_FILENAME.html"

    raml2html "$RAML" > "$HTML"
    if [ $? != 0 ]; then
        echo "error running raml2html" >&2
        cat "$HTML"
        rm "$HTML"
        exit 1
    fi

    #
    # raml2html's out-of-the-box html is great.
    # that said, the statements below are a few minor tweaks
    # that we make to the output of raml2html even better:-)
    #

    # remove odd looking small version number beside the document's title
    sed -i -e 's/<small>version v99.999<\/small>//g' "$HTML"

    ECS_VERSION=$(python -c "import ecs; print ecs.__version__" 2> /dev/null)
    if [ "$ECS_VERSION" == "" ]; then
        ECS_VERSION="UNKNOWN ECS VERSION"
    fi
    sed -i -e "s/%ECS_VERSION%/$ECS_VERSION/g" "$HTML"

    ECS_API_VERSION=$(python -c "import ecs; print ecs.__api_version__" 2> /dev/null)
    if [ "$ECS_API_VERSION" == "" ]; then
        ECS_API_VERSION="UNKNOWN ECS API VERSION"
    fi
    sed -i -e "s/%ECS_API_VERSION%/$ECS_API_VERSION/g" "$HTML"

    # massage the document's title
    sed -i -e "s/API documentation//g" "$HTML"

    if [ "$DEPLOY_API_DOCS" == "1" ]; then
        if [ ! -d "$DEPLOYMENT_DIR" ]; then
            echo "deployment directory '$DEPLOYMENT_DIR' does not exist" >&2
            exit 1
        fi
        sudo cp "$HTML" "$DEPLOYMENT_HTML"
    fi

    return 0
}

rm -f "$SCRIPT_DIR_NAME/api_docs.tar"
rm -f "$SCRIPT_DIR_NAME/*.html"

for FILENAME in $SCRIPT_DIR_NAME/*.raml; do FILENAME=$(basename "$FILENAME"); html_to_raml ${FILENAME%.*}; done

if [ "$DEPLOY_API_DOCS" == "1" ]; then
    sudo mkdir -p "$DEPLOYMENT_DIR/static"
    sudo cp -r "$SCRIPT_DIR_NAME/static" "$DEPLOYMENT_DIR"

    echo "Find API docs @ http://127.0.0.1:$(cat /etc/nginx/sites-enabled/default | grep listen | sed -e 's|^\s*listen\s*||g' | sed -e 's|\s*;\s*$||g')"
fi

if [ "$CREATE_TAR_FILE" == "1" ]; then
    pushd "$SCRIPT_DIR_NAME" > /dev/null
    tar cvf api_docs.tar *.html static
    popd > /dev/null
fi
