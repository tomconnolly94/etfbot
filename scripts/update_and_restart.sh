#!/bin/bash

# get script dir
SCRIPTDIR=$(dirname "$0")

# pull latest code
git pull

# stop the containers
docker stop etfbot

# remove the containers
docker container prune -f

# move to project root
cd $SCRIPTDIR/..

# rebuild and restart containers in daemon mode
docker build -t etfbot .
docker run -p 8080:8080 --name etfbot -d etfbot:latest

cd -
