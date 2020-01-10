FROM docker.io/jfloff/alpine-python:3.8-slim

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

RUN /entrypoint.sh -a dumb-init -r requirements.txt -p gunicorn && python setup.py install
RUN rm /requirements.installed

EXPOSE 9669

CMD ["pasttle-server.py"]
