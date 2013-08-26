#!/bin/bash

PYTHON=`which python`

if [ -z $PYTHON ]; then
    logger "monitor.py: no python found, aborting"
    exit 1
fi

$PYTHON monitor.py

