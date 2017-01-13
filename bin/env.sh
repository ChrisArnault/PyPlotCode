
# move to the script directory

SCRIPT_NAME=${BASH_SOURCE[0]}
SCRIPT_DIR=`dirname ${SCRIPT_NAME}`
ORIGINAL_DIR=${PWD}

cd $SCRIPT_DIR

# add current dir to the PATH

SCRIPT_DIR=`pwd`

export PATH="${SCRIPT_DIR}:${PATH}"

# establish NPAC_ROOT

NPAC_ROOT=`dirname $SCRIPT_DIR`
NPAC_ROOT=`dirname $NPAC_ROOT`

export NPAC_ROOT="${NPAC_ROOT}"

# aliases

alias oval=oval.py
alias anarun=anarun.sh
alias cpstud=copy_to_student.sh

# prepare font cache

python3 -c "import matplotlib.pyplot"

# back to the original directory

cd $ORIGINAL_DIR
