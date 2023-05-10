#!/bin/bash

git pull

# restart docker daemon
../../scripts/docker/rebuild-docker-dameon.sh flask-container

sudo systemctl restart rev-ssh-tunnel-media-grab-webapp.service
