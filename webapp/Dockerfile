# Use the node base image
FROM node:slim

# Set the working directory to /src
WORKDIR /src

# Copy the current directory contents into the container at /app 
ADD . /src

# add python bins
RUN apt-get update -y
RUN apt-get install -y python3
RUN apt-get install -y python3-pip

# Install the dependencies
RUN pip3 install -r requirements.txt
RUN npm install --prefix ./client

# run frontend static file build
RUN client/node_modules/gulp/bin/gulp.js --gulpfile client/build/gulpfile.js build

# config user
#RUN useradd dockuser
#USER dockuser
#RUN chown dockuser:dockuser /tmp/media_grab/data/MediaIndex.json
#USER root

# run the command to start uWSGI
CMD ["uwsgi", "app.ini"]
