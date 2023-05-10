#!/bin/bash

# get script dir
SCRIPTDIR=$(dirname "$0")

# pull latest code
git pull

# move to project root
cd $SCRIPTDIR/..

# activate virtualenv
source venv/bin/activate

# make sure all dependencies are installed 
pip install -r requirements.txt

# cleanup
deactivate
cd -

