#!/usr/bin/env bash
#
# The run a load test analyze_load_test_tsv.py is launched. However, callers
# should not run analyze_load_test_tsv.py directly because:
#
#   1/ you'll generate a harmless but unsettling warning message
#   2/ you'll struggle to get the redirection right
#
# This script eliminates the above problems. To run analyze_load_test_tsv.py
# you'll want to do something like this:
#
#   docker run \
#       -v /tmp/tmp.75LLN1gtrF:/locust-log \
#       -v $PWD:/graphs \
#       simonsdave/ecs-analyze-load-test-tsv \
#       analyze_load_test_tsv.sh 
#

set -e

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

VERBOSE=0

while true
do
    OPTION=`echo ${1:-} | awk '{print tolower($0)}'`
    case "$OPTION" in
        -v)
            shift
            VERBOSE=1
            ;;
        *)
            break
            ;;
    esac
done

if [ $# != 0 ]; then
    echo "usage: `basename $0` [-v]" >&2
    exit 1
fi

# as per https://github.com/matplotlib/matplotlib/issues/5836#issuecomment-212052820
# running the 'python -c ...' to eliminate the message
#
#   Matplotlib is building the font cache using fc-list.
#
# when analyze_load_test_tsv.py runs
python -c 'import matplotlib.pyplot' >& /dev/null

analyze_load_test_tsv.py --graphs=/graphs/load-test-graphs.pdf < /locust-log

exit 0
