#!/usr/bin/env bash

# start cron service 
service cron start

# start uwsgi web server
uwsgi app.ini