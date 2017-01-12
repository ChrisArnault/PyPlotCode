
# establish NPAC_ROOT and add bin to the current PATH

NEW_DIR=`dirname $_`
OLD_DIR=$PWD

cd $NEW_DIR

NEW_DIR=`pwd`

export PATH="${NEW_DIR}:${PATH}"

export NPAC_ROOT=`pwd`
export NPAC_ROOT=`dirname $NPAC_ROOT`
export NPAC_ROOT=`dirname $NPAC_ROOT`

cd $OLD_DIR

# aliases

alias oval=oval.py
alias anarun=anarun.sh