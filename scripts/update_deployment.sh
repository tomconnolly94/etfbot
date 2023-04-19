#!/bin/bash

# get script dir
SCRIPTDIR=$(dirname "$0")

# pull latest code
git pull

# move to project root
cd $SCRIPTDIR/..

# make sure all dependencies are installed 
pip -r requirements.txt

cd -
