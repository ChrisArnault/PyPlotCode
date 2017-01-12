
# establish NPAC_ROOT and add bin to the current PATH

FILE_NAME=$_
FILE_DIR=`dirname ${FILE_NAME}`
OLD_DIR=$PWD

cd $FILE_DIR

FILE_DIR=`pwd`

export PATH="${FILE_DIR}:${PATH}"

export NPAC_ROOT=`pwd`
export NPAC_ROOT=`dirname $NPAC_ROOT`
export NPAC_ROOT=`dirname $NPAC_ROOT`

cd $OLD_DIR

# aliases

alias oval=oval.py
alias anarun=anarun.sh
alias cpstud=copy_to_student.sh