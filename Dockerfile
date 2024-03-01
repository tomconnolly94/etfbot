# Use the node base image
FROM node:slim

ARG PROJDIR=/proj-dir
ARG WEBAPPDIR=$PROJDIR/webapp
ARG INVESTMENTAPPDIR=$PROJDIR/investmentapp

# Set the working directory to $PROJDIR
WORKDIR $PROJDIR

# Copy the current directory contents into the container
ADD . $PROJDIR

# hack to jump over PEP668
ENV PIP_BREAK_SYSTEM_PACKAGES 1

# add python bins
RUN apt-get update -y
RUN apt-get -y install python3 python3-dev
RUN apt-get install -y python3-pip
RUN apt-get install -y cron
RUN apt install libffi-dev

# Install the dependencies
RUN pip3 install -r $WEBAPPDIR/requirements.txt
RUN pip3 install -r $INVESTMENTAPPDIR/requirements.txt
RUN npm install --prefix $WEBAPPDIR/client

# run frontend static file build
RUN $WEBAPPDIR/client/node_modules/gulp/bin/gulp.js --gulpfile $WEBAPPDIR/client/build/gulpfile.js build

# make and config access rights for logging directories
RUN mkdir /var/log/etfbot
RUN chmod 0666 /var/log/etfbot

RUN service cron start
#RUN service cron enable

# install the production env files
COPY ./investmentapp/.prodenv $INVESTMENTAPPDIR/.env
COPY ./webapp/.prodenv $WEBAPPDIR/.env

# install cron job and config access rights
COPY ./investmentapp/cron/etfbot.cronjob /etc/cron.d/etfbot
RUN chmod 0644 /etc/cron.d/etfbot

# expose the port to allow web ui access
EXPOSE 8080

# run the command to start uWSGI
WORKDIR $WEBAPPDIR
CMD ["uwsgi", "app-dev.ini"]
