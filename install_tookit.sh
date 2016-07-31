#!/bin/bash
# Install pds toolkit to local python repo
set -e

PYTHON_PATH=/usr/local/lib/python2.7/dist-packages/pyspider/libs/

if [[! -d $PYTHON_PATH ]]; then
    mkdir $PYTHON_PATH
fi

ABS=$(cd ${0%/*} && echo $PWD/${0##*/})

ln -s $ABS/psdkit $PYTHON_PATH
