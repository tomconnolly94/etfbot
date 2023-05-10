#!/bin/bash

# create virtualenv

# install backend dependencies
source venv/bin/activate
pip install requirements.txt

# install frontend dependencies
cd client
npm install
cd -

#install systemd service