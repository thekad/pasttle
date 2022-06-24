FROM python:3.9-alpine

ENV PASTTLECONF=/app/config/pasttle.ini
ENV APK_PACKAGES=
ENV BUILD_PACKAGES=
ENV PYTHON_PACKAGES=

WORKDIR /app

COPY requirements.txt .
COPY setup.py .
COPY README.rst .
COPY src src
COPY container/pasttle.ini config/pasttle.ini
COPY container/entrypoint.sh /usr/local/sbin/entrypoint

RUN apk update && \
  apk upgrade --no-progress --no-cache && \
  apk add --no-progress --no-cache dumb-init build-base && \
  pip install --no-cache-dir -r requirements.txt && \
  pip install --no-cache-dir gunicorn && \
  python setup.py install && \
  apk del --no-progress build-base

VOLUME /app/config
VOLUME /app/data

EXPOSE 9669

ENTRYPOINT ["/usr/bin/dumb-init"]

CMD ["/usr/local/sbin/entrypoint"]
