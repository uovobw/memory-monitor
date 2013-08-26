#!/bin/bash

FILES="run.sh psutil yaml monitor.py 32bitlib/_psutil_linux.so 32bitlib/_psutil_posix.so memory_monitor.yaml"
TMPDIR="memory_monitor"

mkdir $TMPDIR
cp -av $FILES $TMPDIR

tar zcfp memory_monitor.tar.gz $TMPDIR

rm -rf $TMPDIR
