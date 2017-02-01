
# move to the script directory

SCRIPT_NAME=${BASH_SOURCE[0]}
SCRIPT_DIR=`dirname ${SCRIPT_NAME}`
ORIGINAL_DIR=${PWD}

cd $SCRIPT_DIR

# add current dir to the PATH

SCRIPT_DIR=`pwd`

export PATH="${SCRIPT_DIR}:${PATH}"

# establish NPAC_ROOT

PYPLOTCODE_DIR=`dirname $SCRIPT_DIR`

export NPAC_ROOT=`dirname $PYPLOTCODE_DIR`

# aliases

alias oval=oval.py
alias anarun=anarun.sh
alias anarunx=anarunx.sh
alias cpstud=copy_to_student.sh

# prepare font cache

python3 -c "import matplotlib.pyplot"

# python paths

export PYTHONPATH=${PYPLOTCODE_DIR}/src/skeletons:${PYTHONPATH}
export PYTHONPATH=${PYPLOTCODE_DIR}/src/solutions:${PYTHONPATH}

# data path

export DATAPATH=${PYPLOTCODE_DIR}/data/fits

# back to the original directory

cd $ORIGINAL_DIR
