# Use the node base image
FROM etfbot-dependency-img

ARG PROJDIR=/proj-dir
ARG WEBAPPDIR=$PROJDIR/webapp
ARG INVESTMENTAPPDIR=$PROJDIR/investmentapp
ARG DBDIR=/db

# Set the working directory to $PROJDIR
WORKDIR $PROJDIR

# Copy the current directory contents into the container
ADD . $PROJDIR

# hack to jump over PEP668
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# perform gulp build
RUN $WEBAPPDIR/client/node_modules/gulp/bin/gulp.js --gulpfile $WEBAPPDIR/client/build/gulpfile.js build

# unit testing
RUN python3 -m unittest discover -s investmentapp/Test/
RUN python3 -m unittest discover -s webapp/server/test/
RUN python3 -m unittest discover -s common/test/

# make and config access rights for logging directories
RUN mkdir /var/log/etfbot
RUN chmod 0666 /var/log/etfbot

# install the production env files
COPY ./investmentapp/.prodenv $INVESTMENTAPPDIR/.env
COPY ./webapp/.prodenv $WEBAPPDIR/.env

# install cron job and config access rights
COPY ./investmentapp/cron/etfbot.cronjob /etc/cron.d/etfbot
RUN chmod 0644 /etc/cron.d/etfbot

# install the empty db if it does not exist
RUN mkdir $DBDIR
RUN cp -n ./investmentapp/db/etfbot.base.db $DBDIR/etfbot.db


# expose the port to allow web ui access
EXPOSE 8080

WORKDIR $WEBAPPDIR
ENTRYPOINT ["../entrypoint.sh"]
