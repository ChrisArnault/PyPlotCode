#!/usr/bin/env bash

# This script run a Docker container for anaconda 2 or 3,
# and start the command you ask for.

# The current directory is mounted in the container
# as /work, and you are placed in that directory.

# Invocation : "anarun.sh 2|3 <my command>"
# for example, if I want to start a shell
# within anaconda 3 image : "anarun.sh 3 bash"

# The DISPLAY export require you to predefine MYIP
# and is tested only for MacOSX. Having something which
# works also with linux and windows still TO BE DONE.

if [ "$#" == "0" ]; then
  echo "lacking version and command" ; exit 1 ;
fi

if [ "$1" == "2" ]; then
  img="continuumio/anaconda:4.1.1"
elif [ "$1" == "3" ]; then
  img="continuumio/anaconda3:4.1.1"
else
  echo "bad version $1" ; exit 1 ;
fi
shift

if [ "$#" == "0" ]; then
  echo "lacking command" ; exit 1 ;
else
  cmd="$*"
fi

#export DISPLAY=${MYIP}:0
#xhost + ${MYIP}

echo
#docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw -it --rm -v ${PWD}:/work -w /work ${img} ${cmd}
docker run -it --rm -v ${PWD}:/work -w /work ${img} ${cmd}
echo



