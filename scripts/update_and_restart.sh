#!/bin/bash

# get script dir
SCRIPTDIR=$(dirname "$0")

# pull latest code
git pull

# stop the containers
docker stop etfbot

# remove the previous container
docker rm etfbot

# move to project root
cd $SCRIPTDIR/..

# rebuild and restart containers in daemon mode, relies on volume "etfbot-db-volume" existing
# docker build --no-cache -t etfbot .
docker build -t etfbot .

# exit if docker build fails
if [[ $? -ne 0 ]] ; then
    exit 1
fi

docker run --mount source=etfbot-db-volume,target=/db -p 8080:8080 --name etfbot -d etfbot:latest

# exit if docker run fails
if [[ $? -ne 0 ]] ; then
    exit 2
fi

cd -
