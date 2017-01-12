#!/usr/bin/env bash

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

export DISPLAY=${MYIP}:0
xhost + ${MYIP}

echo
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw -it --rm -v ${PWD}:/work -w /work ${img} ${cmd}
echo



