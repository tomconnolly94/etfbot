#!/bin/bash


# get script dir
SCRIPTDIR=$(dirname "$0")

# move to project root
cd $SCRIPTDIR/..

docker build -t etfbot-dependency-img -f Dockerfile-dependency-img .

cd -