FROM docker.io/jfloff/alpine-python:3.4-slim

ENV PASTTLECONF=/app/config/pasttle.ini
# blank these so they don't reinstall on next runs
ENV PACKAGES=
ENV BUILD_PACKAGES=

ADD requirements.txt /app/requirements.txt
ADD setup.py /app/setup.py
ADD README.rst /app/README.rst
ADD src /app/src
ADD docker.ini /app/config/pasttle.ini

VOLUME /app/config
VOLUME /app/data
WORKDIR /app

RUN /entrypoint.sh -a dumb-init -a python3.4 -b build-base -b python3.4-dev -r requirements.txt -p Paste==2.0.3 && python setup.py install
RUN rm /requirements.installed

EXPOSE 9669

CMD ["pasttle-server.py"]
