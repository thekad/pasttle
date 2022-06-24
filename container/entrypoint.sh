#!/bin/sh -e

# install permanent packages
if [ "x${APK_PACKAGES}" != "x" ]; then
  test -f /apk.installed || apk add --no-progress --no-cache $APK_PACKAGES
  touch /apk.installed
fi

# install system packages required to build python packages
if [ "x${BUILD_PACKAGES}" != "x" ]; then
  test -f /build.installed || apk add --no-progress --no-cache $BUILD_PACKAGES
  touch /build.installed
fi

# install python packages
if [ "x${PYTHON_PACKAGES}" != "x" ]; then
  test -f /python.installed || pip install --no-cache-dir $PYTHON_PACKAGES
  touch /python.installed
fi

# remove requirement build packages
if [ "x${BUILD_PACKAGES}" != "x" ]; then
  test -f /build.installed && apk del --no-progress --purge $BUILD_PACKAGES
fi

/usr/local/bin/pasttle-server.py
